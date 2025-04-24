class TestChunk:
    def test_index(self, client):
        params = {
            "knowledge_name": "test",
            "file_path": "resources/如何本地环境配置.txt",
            "identifier": "test_identifier",
        }

        resp = client.post("/index/chunk", json=params)
        assert resp.status_code == 201

    def test_retrieve_success(self, client):
        params = {
            "knowledge_name": "test",
            "query": "如何本地环境配置",
            "identifier": "test_identifier"
        }

        resp = client.post("/retrieve/chunk", json=params)

        assert resp.status_code == 200
        assert resp.json()["data"][0]['metadata']['source'] == 'local://resources/如何本地环境配置.txt'

    def test_index_oss(self, client):
        params = {
            "knowledge_name": "test",
            "file_path": "user_manual/create_project.md",
            "identifier": "test_identifier",
        }

        resp = client.post("/index/chunk", json=params)
        assert resp.status_code == 201

    def test_retrieve_oss_success(self, client):
        params = {
            "knowledge_name": "test",
            "query": "如何创建 JS 版的项目啊？",
            "identifier": "test_identifier"
        }

        resp = client.post("/retrieve/chunk", json=params)

        assert resp.status_code == 200
        assert resp.json()["data"][0]['metadata']['source'] == 'oss://aarag/user_manual/create_project.md'

    def test_retrieve_not_found(self, client):
        # Input that will cause the retrieval to not find a guide
        params_no_identifier = {
            "knowledge_name": "test",
            "query": "如何本地环境配置？",
        }
        response = client.post("/retrieve/chunk", json=params_no_identifier)
        assert response.status_code == 404

    def test_statistic(self, client):
        # 测试统计接口
        response = client.post(
            "/statistic/knowledge",
            json={"identifier": "test_identifier", "knowledge_name": "test"}
        )
        assert response.status_code == 200
        # 验证返回的统计数据是否包含预期的内容
        assert len(response.json()) > 0
        assert response.json()[0]["source"] == "local://resources/如何本地环境配置.txt"

    def test_statistic_not_found(self, client):
        # 测试统计接口未找到的情况
        response = client.post(
            "/statistic/knowledge",
            json={"identifier": "non_existent_identifier", "knowledge_name": "test"}
        )
        assert response.status_code == 404

    def test_delete_success(self, client):
        # 先获取统计数据以找到要删除的 ID
        statistic_response = client.post(
            "/statistic/knowledge",
            json={"identifier": "test_identifier", "knowledge_name": "test"}
        )
        assert statistic_response.status_code == 200
        # 删除这两个 ID
        for _ in statistic_response.json():
            knowledge_id = _["version"].popitem()[1][0]["id"]
            delete_response = client.post(
                "/delete/knowledge",
                json={"id": knowledge_id, "knowledge_name": "test"}
            )
            assert delete_response.status_code == 204

        # 验证删除后统计数据中不再包含该 ID
        updated_statistic_response = client.post(
            "/statistic/knowledge",
            json={"identifier": "test_identifier", "knowledge_name": "test"}
        )
        assert updated_statistic_response.status_code == 404
