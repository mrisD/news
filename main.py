import datetime
from bson import ObjectId
from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient, ASCENDING, DESCENDING
from crawlabapi import CrawlabApi
"""
将列表页与详情页分开
列表页详情页公用一个更新函数所以即使不是新增配置也会增加定时任务
"""
app = Flask(__name__)

# MongoDB连接配置
MONGO_URI = 'mongodb://localhost:27017/'
DATABASE_NAME = 'me'
COLLECTION_NAME = 'me'

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# 创建索引，提升查询性能
collection.create_index([("modified_time", DESCENDING)])
CrawlabApi=CrawlabApi()
@app.route('/')
def index():
    return render_template('index.html')

# 获取爬虫数据 (带分页、排序功能)
@app.route('/api/crawlers', methods=['GET'])
def get_crawlers():
    try:
        page = int(request.args.get('page', 1))  # 默认第一页
        limit = int(request.args.get('limit', 10))  # 每页默认10条记录
        skip = (page - 1) * limit

        # 支持排序功能
        sort_by = request.args.get('sort_by', 'modified_time')
        sort_order = request.args.get('sort_order', 'desc')

        if sort_order == 'asc':
            sort_direction = ASCENDING
        else:
            sort_direction = DESCENDING

        # 查询并排序
        crawlers_cursor = collection.find().skip(skip).limit(limit).sort(sort_by, sort_direction)
        crawlers = list(crawlers_cursor)

        for crawler in crawlers:
            crawler['_id'] = str(crawler['_id'])
            crawler['created_time'] = crawler['created_time'].strftime('%Y-%m-%d %H:%M:%S')  # 格式化时间
            crawler['modified_time'] = crawler['modified_time'].strftime('%Y-%m-%d %H:%M:%S')  # 格式化时间

        total_count = collection.count_documents({})
        total_pages = (total_count // limit) + (1 if total_count % limit > 0 else 0)

        response_data = {
            "data": crawlers,
            "total": total_count,
            "total_pages": total_pages,
            "current_page": page,
            "limit": limit
        }

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500

# 创建新的爬虫配置
@app.route('/api/crawlers', methods=['POST'])
def create_crawler():
    if request.is_json:
        data = request.get_json()  # 获取JSON数据

        # 添加创建时间和修改时间
        current_time = datetime.datetime.utcnow()
        data['created_time'] = current_time
        data['modified_time'] = current_time

        result = collection.insert_one(data)
        response_data = {
            "message": "Crawler created",
            "id": str(result.inserted_id),
            "data": {k: (str(v) if isinstance(v, ObjectId) else v) for k, v in data.items()}
        }
        return jsonify(response_data), 201
    else:
        return jsonify({"message": "Invalid content type. Expected application/json."}), 400

# 更新爬虫配置
@app.route('/api/crawlers/<string:crawler_id>', methods=['PUT'])
def update_crawler(crawler_id):

    try:
        data = request.get_json()  # 获取前端发送的JSON数据
        result = collection.update_one({"_id": ObjectId(crawler_id)}, {"$set": data})
        if result.modified_count > 0:
            referer = request.headers.get('Referer')  # 获取 Referer 头部信息
            if referer!='http://127.0.0.1:8888/':
                datas=CrawlabApi.addspider(data).json()
                if datas['status']=='ok':
                    timetaskid=datas['data']['_id']
                    # 执行更新操作，添加新的字段
                    result = collection.update_one(
                        {"_id": ObjectId(crawler_id)},  # 根据 _id 查找文档
                        {"$set": {"timetaskid":timetaskid}}  # 添加或更新字段
                    )
                    if result.modified_count > 0:
                        return jsonify({"message": "Crawler updated successfully"}), 200
                    else:
                        return jsonify({"message": "Crawler not found or no changes made"}), 404
                else:
                    return jsonify(datas), 403
            else:
                return jsonify({"message": "Crawler updated successfully"}), 200
        else:
            return jsonify({"message": "No changes made or crawler not found"}), 404
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/api/crawlers/<string:crawler_id>', methods=['GET'])
def get_single_crawler(crawler_id):
    try:
        # 根据ID查找爬虫数据
        crawler = collection.find_one({"_id": ObjectId(crawler_id)})
        if crawler:
            # 格式化时间
            crawler['_id'] = str(crawler['_id'])
            crawler['created_time'] = crawler['created_time'].strftime('%Y-%m-%d %H:%M:%S')
            crawler['modified_time'] = crawler['modified_time'].strftime('%Y-%m-%d %H:%M:%S')
            return jsonify({"data": crawler}), 200
        else:
            return jsonify({"message": "Crawler not found"}), 404
    except Exception as e:
        return jsonify({"message": str(e)}), 500

# 删除爬虫配置
@app.route('/api/crawlers/<string:crawler_id>', methods=['DELETE'])
def delete_crawler(crawler_id):
    result = collection.delete_one({"_id": ObjectId(crawler_id)})
    if result.deleted_count > 0:
        return jsonify({"message": "Crawler deleted"}), 200
    else:
        return jsonify({"message": "Crawler not found"}), 404

#删除指定爬虫的配置
@app.route('/api/crawlers/detaildelete/<string:crawler_id>', methods=['DELETE'])
def delete_detailcrawler(crawler_id):
    # 执行更新操作，删除指定字段
    result = collection.update_one(
        {"_id": ObjectId(crawler_id)},  # 根据 _id 查找文档
        {"$unset": {"new_config": ""}}  # 删除指定字段
    )

    if result.modified_count > 0:
        # 指定 _id 和要查询的字段
        document_id = crawler_id
        query = {"_id": ObjectId(document_id)}  # 查询条件
        projection = {"timetaskid": 1}  # 投影，指定返回的字段
        # 查询文档
        result2 = collection.find_one(query, projection)
        if result2:
            result3=CrawlabApi.deletspider(result2)
            if result3=='ok':
                return jsonify({"message": "Config field deleted"}), 200
            else:
                return jsonify({"message": "Crawler not found or no field to delete"}), 404

    else:
        return jsonify({"message": "Crawler not found or no field to delete"}), 404
#查看指定_id的配置信息
@app.route('/config-details/<string:config_id>', methods=['GET'])
def config_details(config_id):
    try:
        # 从 MongoDB 中根据 ID 查询对应的配置信息
        config = collection.find_one({"_id": ObjectId(config_id)})
        if not config:
            return jsonify({"message": "配置不存在"}), 404

        # 格式化数据（如时间和 ObjectId）
        config['_id'] = str(config['column-id'])
        config['name'] = str(config['resource-name'])
        config['resource_link'] = str(config['resource-link'])
        config['created_time'] = config['created_time'].strftime('%Y-%m-%d %H:%M:%S')
        config['modified_time'] = config['modified_time'].strftime('%Y-%m-%d %H:%M:%S')

        return render_template('details.html', config=config)
    except Exception as e:
        return jsonify({"message": str(e)}), 500





@app.route('/create-config/<crawler_id>')
def create_config_page(crawler_id):
    """
    渲染创建抓取配置页面
    """
    return render_template('creatdetails.html', crawler=crawler_id)



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8888,debug=True)
    #cpolar http 8080
