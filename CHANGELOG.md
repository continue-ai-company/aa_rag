# CHANGELOG


## v0.4.3 (2025-04-25)

### Bug Fixes

- Add user and password parameters to MongoDB connection
  ([`6fe4fe4`](https://github.com/continue-ai-company/aa_rag/commit/6fe4fe4d73ddae4619dcea23c77d8547e5efd178))

### Testing

- Enable OSS index and retrieval tests
  ([`fc5f5fd`](https://github.com/continue-ai-company/aa_rag/commit/fc5f5fd60eba895aed3fd0202a317e6e3111896e))

- Test access to MCP.
  ([`5fd26d6`](https://github.com/continue-ai-company/aa_rag/commit/5fd26d6fe432bb017ee53927ba39323f4e30c3da))

- Update local chunk test to delete multiple knowledge IDs
  ([`57765b7`](https://github.com/continue-ai-company/aa_rag/commit/57765b7fd092f76e3ff0a9c5af6e6a4f720fbc25))


## v0.4.2 (2025-04-09)

### Bug Fixes

- Fixed a bug in tinydb where assertions could not pass when table is empty
  ([`7078074`](https://github.com/continue-ai-company/aa_rag/commit/7078074820c52157437fe3318001f84168394fe6))

- Improve code readability and add conflict check for workflows
  ([`98db479`](https://github.com/continue-ai-company/aa_rag/commit/98db4791a63a4ccb99a92aaf366111dea26c7ae0))

- Secret value for OpenAI API key is not a valid str in utils.py
  ([`23cbb48`](https://github.com/continue-ai-company/aa_rag/commit/23cbb48e1462893d13315a38fe30d3ea84acc8f8))

- Update assets in semantic_release when tag
  ([`69b029c`](https://github.com/continue-ai-company/aa_rag/commit/69b029cfbb68c6ed8e216cccaa3acacadde755ce))

- Update dependencies to latest versions and adjust version constraints
  ([`d3295e6`](https://github.com/continue-ai-company/aa_rag/commit/d3295e696205c73cbeed008d0f155705e91f2110))

### Code Style

- Some format.
  ([`4ac02c3`](https://github.com/continue-ai-company/aa_rag/commit/4ac02c35e310a135672a884125cef229138187fa))

### Continuous Integration

- Disable workflow list_contributors
  ([`cfb8415`](https://github.com/continue-ai-company/aa_rag/commit/cfb841597cf88a85ae683cd5b5b6e65d9550a379))

- Disable workflow release
  ([`1131796`](https://github.com/continue-ai-company/aa_rag/commit/11317963769628bc4b0512e4a806fe14b3ffc75a))

### Testing

- Add local mode test suite.
  ([`3258ded`](https://github.com/continue-ai-company/aa_rag/commit/3258ded8727048a231c0c5300bebadce61915d61))


## v0.4.1 (2025-04-08)

### Bug Fixes

- Add unit tests for add_numbers function
  ([`31a554d`](https://github.com/continue-ai-company/aa_rag/commit/31a554dcb26f96fa429d786100bb4975fbba0d40))

### Continuous Integration

- Add GitHub release configuration to contributors list
  ([`8233153`](https://github.com/continue-ai-company/aa_rag/commit/823315343a8acc86d0249a3cadadc82beb332fd2))

- Add GitHub release configuration to contributors list
  ([`7321591`](https://github.com/continue-ai-company/aa_rag/commit/73215919ed4dfd8c21810bc82ca7277e39ddc773))


## v0.4.0 (2025-04-08)

### Bug Fixes

- Update pre-commit hook entry for linting
  ([`00c2eec`](https://github.com/continue-ai-company/aa_rag/commit/00c2eec247d018f22b8585648ab26e701adfd124))

### Continuous Integration

- Enable workflow publish
  ([`2ccb669`](https://github.com/continue-ai-company/aa_rag/commit/2ccb669e51beaf65160f0107a3d3268228893faf))

### Documentation

- Add Jupyter notebooks for Lancedb and TinyDB data exploration
  ([`8f2c4d7`](https://github.com/continue-ai-company/aa_rag/commit/8f2c4d7db8a30a8d96332b5a9e16969140c42827))

### Features

- Integrate CI/CD workflow and pass all lint.
  ([`921dfcb`](https://github.com/continue-ai-company/aa_rag/commit/921dfcb843d543d9ab18c20fd215bfee70233bb1))


## v0.3.7 (2025-04-01)

### Bug Fixes

- Fix the bug that multilingual can not retrieved success in /qa/retrieve.
  ([`f0339db`](https://github.com/continue-ai-company/aa_rag/commit/f0339db782c61ee273003a07f2feaa0e03404185))

### Chores

- Bump version to 0.3.6.1 and add revision to lock file
  ([`7cc1af7`](https://github.com/continue-ai-company/aa_rag/commit/7cc1af7f0824536bfb0e3c664ee9d414a9f8674a))

- Bump version to 0.3.7 in pyproject.toml
  ([`b668609`](https://github.com/continue-ai-company/aa_rag/commit/b668609500695131cd10b3ba26f0c37a41989813))

### Features

- Enhance retrieval scoring with BM25 and add multilingual support
  ([`e862a58`](https://github.com/continue-ai-company/aa_rag/commit/e862a584e9b87bf2fe90035135187ed704d0ebfb))

### Refactoring

- Remove unused imports from index, retrieve, and exceptions modules
  ([`ec46bf7`](https://github.com/continue-ai-company/aa_rag/commit/ec46bf77aaae2b443f6842fd388f4f5d7b97cbdb))


## v0.3.6 (2025-03-26)

### Bug Fixes

- Add optional project_name parameter to solution function for filtered results
  ([`404ae0f`](https://github.com/continue-ai-company/aa_rag/commit/404ae0fdc64e926ace7a65698d725ea99c99f228))

- Fix the bug that the exception is caused by data query failure.
  ([`42f5326`](https://github.com/continue-ai-company/aa_rag/commit/42f5326940b17a481b7018d61bc62f17681fcbbe))

- Handle None return case in retrieval functions and improve error response
  ([`40cdcdf`](https://github.com/continue-ai-company/aa_rag/commit/40cdcdf0c5e342ab514ceb189d3f60a0d002dbac))

- Update git_url field type to str and improve project metadata handling
  ([`3fbe43c`](https://github.com/continue-ai-company/aa_rag/commit/3fbe43ca47c4440eb972cb455761447ccc7e2a1b))

### Chores

- Bump version to 0.3.5.1 in project and lock files
  ([`77f788c`](https://github.com/continue-ai-company/aa_rag/commit/77f788c0f6f3ccf66c146a0a96c9a0788b846bfa))

- Bump version to 0.3.6 in project and lock files
  ([`5188495`](https://github.com/continue-ai-company/aa_rag/commit/5188495bbe6d8848aa6a0d8bb3f2f47edbee34c1))

### Features

- Add metadata validation and timestamp handling in index and statistic modules
  ([`fcb05c1`](https://github.com/continue-ai-company/aa_rag/commit/fcb05c163d71f88b06514584934d74735a9846e1))


## v0.3.5 (2025-03-25)

### Bug Fixes

- Change error response status code to 500 for exceptions
  ([`5e56298`](https://github.com/continue-ai-company/aa_rag/commit/5e56298861523b694d8d6c394c80f49c29a5166d))

- Ensure cache_file_path is checked for None before validating its prefix
  ([`0c819f0`](https://github.com/continue-ai-company/aa_rag/commit/0c819f0e7f051d62e4237c1fa1ab1806f9d549b9))

- Fixed a bug in OSSResourceInfo model where calculating suffix field values did not take into
  account url field values not None.
  ([`5724bc8`](https://github.com/continue-ai-company/aa_rag/commit/5724bc8e8ae1ca035f8496e899d2fce20e76a26c))

- Handle optional secret key and ensure botocore is available before importing
  ([`ec68906`](https://github.com/continue-ai-company/aa_rag/commit/ec6890613aa5bb4da81627c5a49aa1fa34915f7e))

- Make api_key optional in OpenAI model and enforce validation in model_validator
  ([`32c7e3a`](https://github.com/continue-ai-company/aa_rag/commit/32c7e3a6917c2afa06367cc3f2dc3a605ebccfed))

- Make oss_resource_info optional in document parsing methods
  ([`e674c78`](https://github.com/continue-ai-company/aa_rag/commit/e674c78458a6894ee6ec49f340cb22734915c65b))

- Reorder imports for LightRAG and related functions to improve clarity
  ([`b5dd6e4`](https://github.com/continue-ai-company/aa_rag/commit/b5dd6e453d25869e67e7257439e470a4d0f04d4e))

- Return JSONResponse for 404 status when guide is not found in solution retrieval
  ([`11614eb`](https://github.com/continue-ai-company/aa_rag/commit/11614ebe8078857a2ae9bd3d7d6c5468c5f8450f))

- Safely remove keys from documents in statistic.py
  ([`e9d42ac`](https://github.com/continue-ai-company/aa_rag/commit/e9d42acd6cb1809efd84c5c1a5d384f71a688c91))

- Set default temperature to 0 in OpenAI model configuration
  ([`903832e`](https://github.com/continue-ai-company/aa_rag/commit/903832e5a13b4456c88ad812c4a45ec8270c1576))

- Set default value of expr parameter to None in query method
  ([`8a250f9`](https://github.com/continue-ai-company/aa_rag/commit/8a250f956aac618f9b64a83508c54bc27dcbdbdd))

- Set default_factory for tags in QA schema and update documents example in RetrieveResponse
  ([`5dfc1b0`](https://github.com/continue-ai-company/aa_rag/commit/5dfc1b0f54f031374c85374155f29e30ee8a3860))

- Set max_length and max_capacity for identifier in simple_chunk schema
  ([`2b2ff2c`](https://github.com/continue-ai-company/aa_rag/commit/2b2ff2cd04f385700ad40787c060ac113d02956a))

- Update Body assignment to decode url_content and improve cache_file_path validation
  ([`7b8209c`](https://github.com/continue-ai-company/aa_rag/commit/7b8209c4c7332b4e021bdc2ee662cd28a79bca1a))

- Update delete method to use 'filter' parameter for improved clarity
  ([`98952cd`](https://github.com/continue-ai-company/aa_rag/commit/98952cd1769a67566461dc435616c32a975af51d))

- Update identifier field type to ARRAY and adjust related queries to use array_contains
  ([`6d56fb2`](https://github.com/continue-ai-company/aa_rag/commit/6d56fb2731c763038c2cbd128b85bc194d3d3198))

- Update namespace and table name formatting to use double underscores
  ([`d8e609a`](https://github.com/continue-ai-company/aa_rag/commit/d8e609ac7ad53de7b47ed7e92d1faf91cd7ee113))

### Chores

- Bump version to 0.3.2.0 in pyproject.toml
  ([`950abb2`](https://github.com/continue-ai-company/aa_rag/commit/950abb2c6d1d2abc7f61abe5e292ed4352b3f47d))

- Bump version to 0.3.2.1 in pyproject.toml and uv.lock
  ([`7513294`](https://github.com/continue-ai-company/aa_rag/commit/75132948cea36697ba785d3ce0c57386b94e44ec))

- Bump version to 0.3.3.0 in pyproject.toml and uv.lock
  ([`e283974`](https://github.com/continue-ai-company/aa_rag/commit/e283974aab7449c73a4502d0c9212d7a59290227))

- Bump version to 0.3.3.2 in pyproject.toml and uv.lock
  ([`2bbf00e`](https://github.com/continue-ai-company/aa_rag/commit/2bbf00e7046b2037670d4a4f4b32ad488f11fdd8))

- Bump version to 0.3.3.3 in pyproject.toml and uv.lock
  ([`b43c2a6`](https://github.com/continue-ai-company/aa_rag/commit/b43c2a6ab215ae053cdfd94d67f4997bdf07b7b1))

- Bump version to 0.3.4.0 in pyproject.toml and uv.lock
  ([`bd39591`](https://github.com/continue-ai-company/aa_rag/commit/bd395912e5b48f2eb9641f8ca59d7603d83f2655))

- Bump version to 0.3.5 in project and lock files
  ([`c0b8448`](https://github.com/continue-ai-company/aa_rag/commit/c0b844875c719b4d36239f9073f5de58fe1c7e67))

### Features

- Add BaseIndexParams model and update LightRAGIndexParams and SimpleChunkIndexParams to inherit
  from it
  ([`1bf41b0`](https://github.com/continue-ai-company/aa_rag/commit/1bf41b05bca86eecaefa551f0324f7ec5eb7a33d))

- Add delete router to main application for enhanced functionality
  ([`f29444b`](https://github.com/continue-ai-company/aa_rag/commit/f29444bb9bc8f0482e4362573521b254e8551665))

- Add handler for FileNotFoundError to return a 404 response
  ([`32706f2`](https://github.com/continue-ai-company/aa_rag/commit/32706f20d5166f924fc67bed8c0b9ca1bb2080a5))

- Add response models to index and retrieve endpoints in multiple modules
  ([`31a444e`](https://github.com/continue-ai-company/aa_rag/commit/31a444e1ec3adeccbe5dbd10884aa91e0ff535fd))

- Add statistic router with knowledge and solution endpoints
  ([`66c04c9`](https://github.com/continue-ai-company/aa_rag/commit/66c04c927e44c51960199510f1b9b3052d3021b2))

- Adjust the response code to 404 when nothing is retrieved in qa/retrieve.
  ([`5e1712a`](https://github.com/continue-ai-company/aa_rag/commit/5e1712a334502171aba677eaa2f3b355b67c57d3))

- Bump version to 0.3.1.1 in pyproject.toml and uv.lock
  ([`7b80aef`](https://github.com/continue-ai-company/aa_rag/commit/7b80aef5b66f9bea05fc11d5f6748be992a1672d))

- Bump version to 0.3.1.2 in pyproject.toml
  ([`0066afa`](https://github.com/continue-ai-company/aa_rag/commit/0066afa1e9507e256ef307df596b24d4e38e5782))

- Bump version to 0.3.1.3 in pyproject.toml and uv.lock
  ([`4e9fde1`](https://github.com/continue-ai-company/aa_rag/commit/4e9fde1868bdb76a7eee6083a6db2dfe6405239e))

- Enhance response data model with examples for clarity
  ([`d336080`](https://github.com/continue-ai-company/aa_rag/commit/d336080074949cfd2ee3db1a21906ad82753ed83))

- Implement delete endpoints for QA and solution with request validation
  ([`7244654`](https://github.com/continue-ai-company/aa_rag/commit/7244654ea4824d8c67164992ec43f8f49ee6b6c2))

- Implement JSON-based document selection in QA retrieval process
  ([`c1b83bf`](https://github.com/continue-ai-company/aa_rag/commit/c1b83bf84201be99773274e9df19545e809effcc))

- Refactor statistic endpoints to use SimpleChunkStatisticItem and improve response handling
  ([`76ef683`](https://github.com/continue-ai-company/aa_rag/commit/76ef683dab3f81aa0752d2337d4cdcb3362bd812))

### Refactoring

- Replace json with ast for environment info parsing and update prompt template for compatibility
  checks
  ([`5a642d3`](https://github.com/continue-ai-company/aa_rag/commit/5a642d3359721a8f034a450f6bfdf08d8b904a10))

- Standardize all response formats.
  ([`67c7310`](https://github.com/continue-ai-company/aa_rag/commit/67c7310af303aa00f3329111dd7f6d884d194814))

- Update import statements and replace field_validator with model_validator in settings.py
  ([`1e675ae`](https://github.com/continue-ai-company/aa_rag/commit/1e675ae337060fbfe253aed71f7696ed027283e9))


## v0.3.1 (2025-03-05)

### Features

- Bump version to 0.3.1 in pyproject.toml and uv.lock
  ([`66846d9`](https://github.com/continue-ai-company/aa_rag/commit/66846d9974efea7ad2b7626f22460ba9d738ab10))

- Enhance image storage functionality by adding extra parameter for MD5 calculation
  ([`065170d`](https://github.com/continue-ai-company/aa_rag/commit/065170daa4374a46d7bea3036ab9340fed891a32))


## v0.3.0 (2025-03-05)

### Bug Fixes

- Change model_config to forbid extra fields in SimpleChunkIndexItem
  ([`551b84c`](https://github.com/continue-ai-company/aa_rag/commit/551b84c2910395621bd4269d0d247cd8ce4cac92))

- Correct delete method parameters and improve collection truncation logic
  ([`f10d3a2`](https://github.com/continue-ai-company/aa_rag/commit/f10d3a2fb4b23347b7e95b668062677ba45a9ab2))

- Enhance load_env function to support environment-specific defaults and improve dotenv integration
  ([`5b73146`](https://github.com/continue-ai-company/aa_rag/commit/5b73146c0d0b75e6275b31b89f8d7cde5e4d5c80))

- Update _build_store method to support string input for mode parameter
  ([`cf83338`](https://github.com/continue-ai-company/aa_rag/commit/cf83338478eb163525692d2353fd09777251d46a))

- Update error messages for online service installation and refactor secret handling.
  ([`b1c6c76`](https://github.com/continue-ai-company/aa_rag/commit/b1c6c763279cf2662bdb48b3e6d741910b6f9454))

- Update error messages to reflect correct package name and improve clarity
  ([`ef4ef69`](https://github.com/continue-ai-company/aa_rag/commit/ef4ef69184cbc5f53b8f280bcf62dc7ff91c942a))

### Chores

- Update .gitignore to exclude storage directory and config.ini file
  ([`1c4dc0e`](https://github.com/continue-ai-company/aa_rag/commit/1c4dc0e24c425032d5c86ffeda75f4e61843ca91))

### Code Style

- Standardize string quotes and formatting in csv2json.py
  ([`56792da`](https://github.com/continue-ai-company/aa_rag/commit/56792da4ed72debb085ebcb975eb1f38da8f8b99))

### Documentation

- Clean up formatting in delete method and remove unnecessary blank line in upsert method
  ([`f2f4cbd`](https://github.com/continue-ai-company/aa_rag/commit/f2f4cbd8a1363a3e3461791449a44553ae70a1d1))

### Features

- Add API key validation and make OSS access/secret keys optional.
  ([`fc24e39`](https://github.com/continue-ai-company/aa_rag/commit/fc24e39fab38e72065a7eac005acf2be35e2dc4e))

- Add csv2json script for converting CSV data to deployment JSON format
  ([`987222d`](https://github.com/continue-ai-company/aa_rag/commit/987222deaf53077030cb59dc307877d4dc565217))

- Add multimodal support with image storage and retrieval functionality
  ([`fe1bfb5`](https://github.com/continue-ai-company/aa_rag/commit/fe1bfb558dc6f120e9e43349e7174f7b9354880a))

- Bump version to 0.3.0 in pyproject.toml and uv.lock
  ([`92c9bb4`](https://github.com/continue-ai-company/aa_rag/commit/92c9bb4dd1a2f33205f1ae361150bcfc5308ae4c))

- Enhance SimpleChunk engine with JSON merge support in upsert and improve parameter handling
  ([`80df07d`](https://github.com/continue-ai-company/aa_rag/commit/80df07d73eb38f1e70901e79aec8dcc84f7808b5))

- Implement LightRAG engine with indexing and retrieval capabilities, update storage settings, and
  enhance parsing functionality
  ([`6ba0203`](https://github.com/continue-ai-company/aa_rag/commit/6ba020377392c8bd24747a5b975daebbb0c59726))

- Implement MarkitDownParser for enhanced file parsing and integrate with chunk indexing
  ([`173fc5d`](https://github.com/continue-ai-company/aa_rag/commit/173fc5d804645ccf6f9c8b0d96b311fc0e59bd94))

- Refactor knowledge base classes to improve initialization and compatibility checks
  ([`03193d5`](https://github.com/continue-ai-company/aa_rag/commit/03193d5686cd80b3c1ac8faec8b420c20f6bdeef))

### Refactoring

- Adjust project structure and supports the creation of private knowledge bases.
  ([`21a4898`](https://github.com/continue-ai-company/aa_rag/commit/21a489805c4db095431845dbee779044b6ba7238))


## v0.2.2 (2025-02-22)

### Documentation

- Update installation instructions and remove outdated options
  ([`d2646cc`](https://github.com/continue-ai-company/aa_rag/commit/d2646cca5973a759f9be873a456cdaf041fa4e97))

### Features

- Add secret masking functionality to model output in FastAPI.
  ([`5b6eda7`](https://github.com/continue-ai-company/aa_rag/commit/5b6eda7547d051c43194a00cd73f45381815cb46))

- Enhance database connection handling and update configuration validation
  ([`ad74e15`](https://github.com/continue-ai-company/aa_rag/commit/ad74e153f720cd0e1210fc4850285751086718ca))

- Move secret masking functionality to settings module and refactor implementation
  ([`c57d9e4`](https://github.com/continue-ai-company/aa_rag/commit/c57d9e429e1dfda241670dd6a6b67f5a7c5fef8c))


## v0.2.1 (2025-02-21)

### Bug Fixes

- Fix the bug that /solution/retrieve interface can not to return a response object correctly.
  ([`4964493`](https://github.com/continue-ai-company/aa_rag/commit/496449302844516a32bc7f18b3015ed99eadd2bf))

- Fix the bug that can not load .env file when installing package via pip and delete the method of
  modifying default values through command line parameters.
  ([`17eaf5b`](https://github.com/continue-ai-company/aa_rag/commit/17eaf5b2346cd6b0fd9ba73a379046f9550455d5))

- Fixed a bug where milvus wouldn't load properly
  ([`bc5ed78`](https://github.com/continue-ai-company/aa_rag/commit/bc5ed7864886d741a919630cb67ffc2a5bde808f))

### Chores

- Bump project version to 0.1.3.1 and update documentation.
  ([`afe9932`](https://github.com/continue-ai-company/aa_rag/commit/afe99327a2c5f2fa4a28e65c8a26c0a1cd2676db))

- Bump version to 0.2.1 and update dependencies for boto3 and propcache.
  ([`fce857e`](https://github.com/continue-ai-company/aa_rag/commit/fce857ecc0d39557a06433c138586396b8bce9f0))

- Update configuration documentation and bump project version to 0.2.0
  ([`e1abd6f`](https://github.com/continue-ai-company/aa_rag/commit/e1abd6faea41a778351a64539f7b658edd82825c))

- Update package versions and bump project version to 0.1.3.0.
  ([`05c9838`](https://github.com/continue-ai-company/aa_rag/commit/05c983895091e08e5d830835452334ce285e1b12))

### Documentation

- Update CONFIGURATION.md
  ([`dcdb10c`](https://github.com/continue-ai-company/aa_rag/commit/dcdb10c7b39fd159f1ddf18be8f2078d5ec2e1fd))

- Update CONFIGURATION.md
  ([`285c310`](https://github.com/continue-ai-company/aa_rag/commit/285c3101d4bc21fdedd4b9703ac50d57b73ef774))

- Update README.md
  ([`0387016`](https://github.com/continue-ai-company/aa_rag/commit/0387016f3d843c43bf90c1f62d61087cdc44b2aa))

- Update README.md
  ([`e7ea88a`](https://github.com/continue-ai-company/aa_rag/commit/e7ea88a518bedd530009ea5df7ace9eed3f48114))

- Update version.
  ([`35f4768`](https://github.com/continue-ai-company/aa_rag/commit/35f4768825bfecbe79ac5b3e0c4a5228e074829c))

- Update version.
  ([`7d12fb8`](https://github.com/continue-ai-company/aa_rag/commit/7d12fb8ecd14fe9df8cf9018d4fd6fa27311e129))

### Features

- Add Milvus as a vector database backend and refactor related components
  ([`7e84142`](https://github.com/continue-ai-company/aa_rag/commit/7e84142e0b7948b8e379ab4807a807027cf392a5))

- Add MongoDB as a NoSQL database backend and implement singleton pattern
  ([`f2b93da`](https://github.com/continue-ai-company/aa_rag/commit/f2b93da7b0ab71c6952f34f74397197b789a1b74))

- Change the db.relation configuration entry to db.nosql.
  ([`11b5998`](https://github.com/continue-ai-company/aa_rag/commit/11b599850cb3749ceb2790c4370c55527cbdcaa5))

- Implement TinyDB as NoSQL database backend and refactor SolutionKnowledge class
  ([`2d7553d`](https://github.com/continue-ai-company/aa_rag/commit/2d7553d7ad491c2bbd1bcae2c397954894ea2ae3))

- Improve qa knowledge base algorithm.
  ([`f10c855`](https://github.com/continue-ai-company/aa_rag/commit/f10c8551adc9145ede6083cf5954aff06743da25))

- Update OSS integration with S3 support and enhance file parsing functionality.
  ([`f9df27c`](https://github.com/continue-ai-company/aa_rag/commit/f9df27cd272b6ba3c8d26632c6164884e2fda1df))

### Refactoring

- Adjust the format of incoming data.
  ([`fad1a8f`](https://github.com/continue-ai-company/aa_rag/commit/fad1a8f2af1032be76bab3d0d15170b7477fa302))

- Adjust the startup mode.
  ([`b618578`](https://github.com/continue-ai-company/aa_rag/commit/b618578198fa2175cfb7c46dc6a10e383c4cc63a))

- Modify IndexResponse.Data model.
  ([`115f3bd`](https://github.com/continue-ai-company/aa_rag/commit/115f3bd09e296003511bbada255f403dfda7a324))

- Replace Enum types with string types for embedding and language models.
  ([`94c89da`](https://github.com/continue-ai-company/aa_rag/commit/94c89daf7bc6341de0bc0642791c11b4906957c6))

- Unifies vector database operations and abstracts them into objects.
  ([`4e502e2`](https://github.com/continue-ai-company/aa_rag/commit/4e502e29d918b5b51d1147019120275d1fb8a1e2))


## v0.1.2 (2025-01-21)

### Bug Fixes

- Fix the bug that can not create lancedb directory when the first time to store.
  ([`5daca94`](https://github.com/continue-ai-company/aa_rag/commit/5daca94b7e0a644637738294556cd49f3418c93d))

- Fix the bug that env variables cannot be loaded correctly.
  ([`5e8013c`](https://github.com/continue-ai-company/aa_rag/commit/5e8013c0e137a32bea3fd7f3c5e5225ae9c33aa8))

### Code Style

- Adjust some default variable name.
  ([`3e7188c`](https://github.com/continue-ai-company/aa_rag/commit/3e7188cd7f6bc4a966fd197e6fe4f1c0990f35a0))

### Documentation

- Upadte README.md
  ([`88f8ced`](https://github.com/continue-ai-company/aa_rag/commit/88f8cedca707b042a96adbf1547cff61009ce263))

- Update .gitignore.
  ([`2e708ee`](https://github.com/continue-ai-company/aa_rag/commit/2e708ee4c20808676c90ddb22804ae776aa4b02a))

- Update README.md
  ([`cf2ae98`](https://github.com/continue-ai-company/aa_rag/commit/cf2ae98263e7a90f5b4d4d1ebbce7825ffd95f1c))

- Update the SolutionKnowledge class annotation.
  ([`4aeb070`](https://github.com/continue-ai-company/aa_rag/commit/4aeb07099ea841e9812a809b2dae7b13b074d718))

- Update uv.lock.
  ([`46af111`](https://github.com/continue-ai-company/aa_rag/commit/46af111dfcb8a77b4637976903fbd523c4209218))

### Features

- Add index algorithm of Solution Knowledge Base.
  ([`96b5c4c`](https://github.com/continue-ai-company/aa_rag/commit/96b5c4cd4e8f0f233ceba4ee160808941792382a))

- Add interface /default displays all parsed default parameters.
  ([`bff31a1`](https://github.com/continue-ai-company/aa_rag/commit/bff31a13daa101a4fc3abcb631c8f0b020240c93))

- Add qa knowledge base router.
  ([`4a0a6f4`](https://github.com/continue-ai-company/aa_rag/commit/4a0a6f44ce15df2fe3eed9c0035a0c16a3c1a678))

- Add retrieve algorithm of Solution Knowledge Base.
  ([`ee9beea`](https://github.com/continue-ai-company/aa_rag/commit/ee9beea3af2d898369ea0a917ebdc51d0e675dc2))

- Add solution knowledge base router.
  ([`75c4222`](https://github.com/continue-ai-company/aa_rag/commit/75c422287e1648607ab36217615fb27fb8757147))

- Added command line support.
  ([`597be18`](https://github.com/continue-ai-company/aa_rag/commit/597be18281fc4a69926d84d2d033c6f79a7f520c))

- Refactoring project based on fastapi.
  ([`b05d805`](https://github.com/continue-ai-company/aa_rag/commit/b05d8058285d6cee33f70e9b330b90194e3c23e4))

- Remove default parameters in default.py, and pydantic_setting controls global parameters instead.
  ([`0ad5602`](https://github.com/continue-ai-company/aa_rag/commit/0ad5602bda7a920c5bfedaf1259709e8f60b48ad))

- Supports catching exceptions for environment variable exceptions.
  ([`9327fac`](https://github.com/continue-ai-company/aa_rag/commit/9327fac0c0a91ebaa637cbe7ec4cd5e491a25657))

### Refactoring

- Adjust the app entrypoint.
  ([`2b92cc3`](https://github.com/continue-ai-company/aa_rag/commit/2b92cc3a338f613736545683d8788aba668c1267))

- Adjust the input to the SolutionKnowledge index method.
  ([`3378c2b`](https://github.com/continue-ai-company/aa_rag/commit/3378c2bd4c43bd5cbcb17a929f0e3367a36ef416))
