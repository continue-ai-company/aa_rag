class TestSolution:
    def test_root(self, client):
        response = client.get("/solution/")
        assert response.status_code == 200
        assert response.json() == {
            "built_in": True,
            "description": "项目部署方案库",
        }

    def test_index(self, client):
        # Sample input that conforms to the SolutionIndexItem schema
        item_data = {
            "env_info": {"platform": "darwin", "arch": "arm64"},
            "project_meta": {"name": "PaddleOCR", "url": "github.com/test/run??"},
            "procedure": "春天花儿开，小鸟依然自在地飞翔",
        }
        response = client.post("/solution/index", json=item_data)
        assert response.status_code == 201

    def test_retrieve_success(self, client):
        # First index some data to retrieve
        index_data = {
            "env_info": {"platform": "linux", "arch": "x86_64"},
            "project_meta": {"name": "TestProject", "url": "github.com/test/project"},
            "procedure": "Step 1: Install dependencies\nStep 2: Build project\nStep 3: Run tests",
        }
        client.post("/solution/index", json=index_data)

        # Sample input that conforms to the SolutionRetrieveItem schema
        item_data = {
            "env_info": {"platform": "linux", "arch": "x86_64"},
            "project_meta": {
                "name": "TestProject",
            },
        }
        response = client.post("/solution/retrieve", json=item_data)
        assert response.status_code == 200
        # Verify at least some content from the indexed data appears in the response
        assert "Step 1: Install dependencies" in str(response.json())

    def test_retrieve_not_found(self, client):
        # Input that will cause the retrieval to not find a guide
        item_data = {
            "env_info": {"platform": "windows", "arch": "arm64"},
            "project_meta": {"name": "PaddleOCR", "url": "github.com/test/run"},
        }
        response = client.post("/solution/retrieve", json=item_data)
        assert response.status_code == 404
        assert response.json()["message"] == "Guide not found"

    def test_statistic(self, client):
        response = client.get("/solution/statistic")
        assert response.status_code == 200
        # At this point we should have at least 2 solutions indexed
        assert len(list(response.json())) >= 2

    def test_delete_success(self, client):
        # Get statistics to find an ID to delete
        statistic_result = client.get("/solution/statistic?project_name=TestProject")
        project_name, project_info = statistic_result.json().popitem()
        project_id = project_info["project_id"]
        first_guide = project_info["guides"][0]

        params = {
            "id": project_id,
            "platform": first_guide["compatible_env"]["platform"],
            "arch": first_guide["compatible_env"]["arch"],
        }

        response = client.post("/solution/delete", json=params)
        assert response.status_code == 204

        # Verify one item was deleted
        updated_statistic_result = client.get("/solution/statistic?project_name=TestProject")
        assert len(updated_statistic_result.json()['TestProject']['guides']) == 0

    def test_delete_failed(self, client):
        # Try to delete with a non-existent ID
        params = {
            "id": "non_existent_id",
            "platform": "non_existent_platform",
            "arch": "non_existent_arch",
        }

        response = client.post("/solution/delete", json=params)
        # The API should handle this gracefully
        assert response.status_code == 404
