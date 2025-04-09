class TestQA:
    def test_root(self, client):
        response = client.get("/qa/")
        assert response.status_code == 200
        assert response.json() == {
            "built_in": True,
            "description": "问题/解决方案库",
        }

    def test_index(self, client):
        # Sample input that conforms to the QAIndexItem schema
        item_data = {
            "error_desc": "RuntimeError: CUDA out of memory",
            "error_solution": "Reduce batch size or model size to fit in GPU memory",
            "tags": ["cuda", "memory", "pytorch"],
        }
        response = client.post("/qa/index", json=item_data)
        assert response.status_code == 201

    def test_retrieve_success(self, client):
        # First index some data to retrieve
        index_data = {
            "error_desc": "ImportError: No module named tensorflow",
            "error_solution": "Install tensorflow using pip install tensorflow",
            "tags": ["import", "tensorflow", "installation"],
        }
        client.post("/qa/index", json=index_data)

        # Sample input that conforms to the QARetrieveItem schema
        item_data = {
            "error_desc": "ImportError: No module named tensorflow",
            "tags": ["tensorflow"],
        }
        response = client.post("/qa/retrieve", json=item_data)
        assert response.status_code == 200
        assert response.json()["data"][0]['page_content'] == "ImportError: No module named tensorflow"

    def test_statistic(self, client):
        response = client.get("/qa/statistic")
        assert response.status_code == 200
        assert len(list(response.json())) == 2

    def test_delete_success(self, client):
        statistic_result = client.get("/qa/statistic")
        first_id = statistic_result.json()[0]['id']

        params = {
            "id": first_id
        }

        response = client.get("/qa/delete", params=params)
        assert response.status_code == 204

        deleted_statistic_result = client.get("/qa/statistic")
        assert len(list(deleted_statistic_result.json())) == 1

    def test_delete_failed(self, client):
        crt_statistic_result_len = 1

        params = {
            "id": "1234"
        }

        client.get("/qa/delete", params=params)

        deleted_statistic_result = client.get("/qa/statistic")

        assert len(list(deleted_statistic_result.json())) == crt_statistic_result_len
