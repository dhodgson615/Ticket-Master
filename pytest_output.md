```
============================= test session starts ==============================
platform darwin -- Python 3.12.11, pytest-8.4.2, pluggy-1.6.0
rootdir: /Users/dhodgson/Desktop/Ticket-Master
configfile: pyproject.toml
plugins: anyio-4.11.0, cov-7.0.0
collected 568 items

tests/test_app.py ...........F..F...........                             [  4%]
tests/test_auth.py ..........FF..F.FF..F.                                [  8%]
tests/test_branch.py ........                                            [  9%]
tests/test_colors.py .............F.....F..F..FFF.F.FFFFF.FFFFFFF...FF.. [ 18%]
F                                                                        [ 19%]
tests/test_commit.py ..F..........                                       [ 21%]
tests/test_data_scraper.py FF.F.FFFFFFFF.FFFFFFFFFFFFFFFFFFFFF           [ 27%]
tests/test_database.py FFFF..F                                           [ 28%]
tests/test_edge_cases.py FFFFFFFFFFFFFFFFFF                              [ 31%]
tests/test_examples.py ............                                      [ 33%]
tests/test_git_objects.py .F.F....F.FFF...FFFFF..FFFFF                   [ 38%]
tests/test_github_utils.py ..F.F...F.FFFFFFFF........F...                [ 44%]
tests/test_init.py ..............                                        [ 46%]
tests/test_integration.py ..FF                                           [ 47%]
tests/test_issue.py ........................FF........................   [ 56%]
tests/test_llm.py ..F.....FFFFF.FFFFFFFFFFFFFFFFFFFFFFFFF.F.F            [ 63%]
tests/test_main.py ......F.........FFF.FFFFF                             [ 68%]
tests/test_new_classes.py FFFF..FFFFFFFFFFFFFFFFF..FF.FFFFFFFF..FFF      [ 75%]
tests/test_ollama_tools.py FFFFFFFFFFFFFFFFFFF..FFFFFFFFFFFF.            [ 81%]
tests/test_performance.py FFF..F.......                                  [ 83%]
tests/test_pipe.py FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF...F                  [ 89%]
tests/test_prompt.py FFFFFFFFFFFF                                        [ 92%]
tests/test_pull_request.py .FFFFF.F.F....F...............                [ 97%]
tests/test_repository.py ....F.....F....                                 [100%]

=================================== FAILURES ===================================
_________ TestGenerateIssuesRoute.test_generate_issues_with_local_path _________

self = <tests.test_app.TestGenerateIssuesRoute object at 0x10a7f7e90>
mock_exists = <MagicMock name='exists' id='4475372656'>
mock_generate = <MagicMock name='generate_sample_issues' id='4475831552'>
mock_repository = <MagicMock name='Repository' id='4475843120'>
mock_load_config = <MagicMock name='load_config' id='4475928896'>
mock_github_utils = <MagicMock name='GitHubUtils' id='4475932688'>

    @patch("app.GitHubUtils")
    @patch("app.load_config")
    @patch("app.Repository")
    @patch("app.generate_sample_issues")
    @patch("os.path.exists")
    def test_generate_issues_with_local_path(
        self,
        mock_exists,
        mock_generate,
        mock_repository,
        mock_load_config,
        mock_github_utils,
    ):
        """Test generate_issues with valid local path."""
        # Setup mocks
        mock_exists.return_value = True
        mock_load_config.return_value = {
            "github": {"token": "test_token"},
            "issue_generation": {"max_issues": 5},
            "repository": {},
            "llm": {"provider": "mock"},
        }
    
        mock_utils_instance = Mock()
        mock_utils_instance.parse_github_url.return_value = self.test_repo
        mock_utils_instance.is_public_repository.return_value = True
        mock_github_utils.return_value = mock_utils_instance
    
        mock_repo_instance = Mock()
        mock_repo_instance.analyze.return_value = {
            "commits": [],
            "file_changes": {"new_files": [], "modified_files": {}},
            "summary": {
                "commit_count": 0,
                "files_modified": 0,
                "files_added": 0,
            },
        }
        mock_repository.return_value = mock_repo_instance
    
        mock_generate.return_value = []
    
        form_data = self.form_data.copy()
        form_data["repository_path"] = "/valid/path"
    
        with app.app.test_client() as client:
            with patch("app.render_template") as mock_render:
                mock_render.return_value = "mocked_result"
    
                response = client.post("/generate", data=form_data)
    
>               assert response.status_code == 200
E               assert 302 == 200
E                +  where 302 = <WrapperTestResponse streamed [302 FOUND]>.status_code

tests/test_app.py:273: AssertionError
_______ TestGenerateIssuesRoute.test_generate_issues_success_public_repo _______

self = <tests.test_app.TestGenerateIssuesRoute object at 0x10a830350>
mock_generate = <MagicMock name='generate_sample_issues' id='4476504832'>
mock_repository = <MagicMock name='Repository' id='4476514240'>
mock_load_config = <MagicMock name='load_config' id='4476518176'>
mock_github_utils = <MagicMock name='GitHubUtils' id='4476275504'>

    @patch("app.GitHubUtils")
    @patch("app.load_config")
    @patch("app.Repository")
    @patch("app.generate_sample_issues")
    def test_generate_issues_success_public_repo(
        self,
        mock_generate,
        mock_repository,
        mock_load_config,
        mock_github_utils,
    ):
        """Test successful issue generation for public repository."""
        # Setup mocks
        mock_load_config.return_value = {
            "github": {"token": "test_token"},
            "issue_generation": {"max_issues": 5},
            "repository": {},
            "llm": {"provider": "mock"},
        }
    
        mock_utils_instance = Mock()
        mock_utils_instance.parse_github_url.return_value = self.test_repo
        mock_utils_instance.is_public_repository.return_value = True
        mock_utils_instance.clone_repository.return_value = "/tmp/test_repo"
        mock_github_utils.return_value = mock_utils_instance
    
        mock_repo_instance = Mock()
        mock_repo_instance.analyze.return_value = {
            "commits": [{"short_hash": "abc123", "summary": "Test commit"}],
            "file_changes": {"new_files": ["test.py"], "modified_files": {}},
            "summary": {
                "commit_count": 1,
                "files_modified": 0,
                "files_added": 1,
            },
        }
        mock_repository.return_value = mock_repo_instance
    
        # Mock issue generation
        mock_issue = Mock()
        mock_issue.title = "Test Issue"
        mock_issue.description = "Test Description"
        mock_generate.return_value = [mock_issue]
    
        with app.app.test_client() as client:
            with patch("app.render_template") as mock_render:
                mock_render.return_value = "success_page"
    
                response = client.post("/generate", data=self.form_data)
    
>               assert response.status_code == 200
E               assert 302 == 200
E                +  where 302 = <WrapperTestResponse streamed [302 FOUND]>.status_code

tests/test_app.py:380: AssertionError
______ TestAuthenticationGitHubIntegration.test_create_client_with_token _______

self = Authentication(token_set=True, env_token_set=False, has_token=True)
token = None

    def create_client(self, token: Optional[str] = None) -> Github:
        """Create authenticated GitHub client."""
        auth_token = token or self.get_token()
    
        try:
            auth = Auth.Token(auth_token)
            github_client = Github(auth=auth)
    
            # Test authentication by getting user info
            user = github_client.get_user()
>           self.logger.info(f"Authenticated as GitHub user: {user.login}")
                                                              ^^^^^^^^^^

src/ticket_master_consolidated.py:283: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
.venv/lib/python3.12/site-packages/github/AuthenticatedUser.py:294: in login
    self._completeIfNotSet(self._login)
.venv/lib/python3.12/site-packages/github/GithubObject.py:606: in _completeIfNotSet
    self._completeIfNeeded()
.venv/lib/python3.12/site-packages/github/GithubObject.py:610: in _completeIfNeeded
    self.__complete()
.venv/lib/python3.12/site-packages/github/GithubObject.py:615: in __complete
    headers, data = self._requester.requestJsonAndCheck("GET", self._url.value, headers=self.__completeHeaders)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.venv/lib/python3.12/site-packages/github/Requester.py:623: in requestJsonAndCheck
    return self.__check(
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <github.Requester.Requester object at 0x10ad279b0>, status = 401
responseHeaders = {'access-control-allow-origin': '*', 'access-control-expose-headers': 'ETag, Link, Location, Retry-After, X-GitHub-OTP...X-GitHub-Request-Id, Deprecation, Sunset', 'connection': 'close', 'content-security-policy': "default-src 'none'", ...}
output = '{\r\n  "message": "Bad credentials",\r\n  "documentation_url": "https://docs.github.com/rest",\r\n  "status": "401"\r\n}'

    def __check(
        self,
        status: int,
        responseHeaders: dict[str, Any],
        output: str,
    ) -> tuple[dict[str, Any], Any]:
        data = self.__structuredFromJson(output)
        if status >= 400:
>           raise self.createException(status, responseHeaders, data)
E           github.GithubException.BadCredentialsException: 401 {"message": "Bad credentials", "documentation_url": "https://docs.github.com/rest", "status": "401"}

.venv/lib/python3.12/site-packages/github/Requester.py:853: BadCredentialsException

During handling of the above exception, another exception occurred:

self = <tests.test_auth.TestAuthenticationGitHubIntegration object at 0x10a852f00>
mock_github_class = <MagicMock name='Github' id='4476662464'>

    @patch("ticket_master_consolidated.Github")
    def test_create_client_with_token(self, mock_github_class):
        """Test creating GitHub client with token."""
        mock_github = MagicMock()
        mock_user = MagicMock()
        mock_user.login = "test_user"
        mock_github.get_user.return_value = mock_user
        mock_github_class.return_value = mock_github
    
        auth = Authentication("test_token")
>       client = auth.create_client()
                 ^^^^^^^^^^^^^^^^^^^^

tests/test_auth.py:100: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = Authentication(token_set=True, env_token_set=False, has_token=True)
token = None

    def create_client(self, token: Optional[str] = None) -> Github:
        """Create authenticated GitHub client."""
        auth_token = token or self.get_token()
    
        try:
            auth = Auth.Token(auth_token)
            github_client = Github(auth=auth)
    
            # Test authentication by getting user info
            user = github_client.get_user()
            self.logger.info(f"Authenticated as GitHub user: {user.login}")
    
            return github_client
    
        except BadCredentialsException as e:
>           raise GitHubAuthError(f"Invalid GitHub credentials: {e}")
E           src.ticket_master_consolidated.GitHubAuthError: Invalid GitHub credentials: 401 {"message": "Bad credentials", "documentation_url": "https://docs.github.com/rest", "status": "401"}

src/ticket_master_consolidated.py:288: GitHubAuthError
_ TestAuthenticationGitHubIntegration.test_create_client_token_parameter_overrides_instance _

self = Authentication(token_set=True, env_token_set=False, has_token=True)
token = 'override_token'

    def create_client(self, token: Optional[str] = None) -> Github:
        """Create authenticated GitHub client."""
        auth_token = token or self.get_token()
    
        try:
            auth = Auth.Token(auth_token)
            github_client = Github(auth=auth)
    
            # Test authentication by getting user info
            user = github_client.get_user()
>           self.logger.info(f"Authenticated as GitHub user: {user.login}")
                                                              ^^^^^^^^^^

src/ticket_master_consolidated.py:283: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
.venv/lib/python3.12/site-packages/github/AuthenticatedUser.py:294: in login
    self._completeIfNotSet(self._login)
.venv/lib/python3.12/site-packages/github/GithubObject.py:606: in _completeIfNotSet
    self._completeIfNeeded()
.venv/lib/python3.12/site-packages/github/GithubObject.py:610: in _completeIfNeeded
    self.__complete()
.venv/lib/python3.12/site-packages/github/GithubObject.py:615: in __complete
    headers, data = self._requester.requestJsonAndCheck("GET", self._url.value, headers=self.__completeHeaders)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.venv/lib/python3.12/site-packages/github/Requester.py:623: in requestJsonAndCheck
    return self.__check(
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <github.Requester.Requester object at 0x10ae30d10>, status = 401
responseHeaders = {'access-control-allow-origin': '*', 'access-control-expose-headers': 'ETag, Link, Location, Retry-After, X-GitHub-OTP...X-GitHub-Request-Id, Deprecation, Sunset', 'connection': 'close', 'content-security-policy': "default-src 'none'", ...}
output = '{\r\n  "message": "Bad credentials",\r\n  "documentation_url": "https://docs.github.com/rest",\r\n  "status": "401"\r\n}'

    def __check(
        self,
        status: int,
        responseHeaders: dict[str, Any],
        output: str,
    ) -> tuple[dict[str, Any], Any]:
        data = self.__structuredFromJson(output)
        if status >= 400:
>           raise self.createException(status, responseHeaders, data)
E           github.GithubException.BadCredentialsException: 401 {"message": "Bad credentials", "documentation_url": "https://docs.github.com/rest", "status": "401"}

.venv/lib/python3.12/site-packages/github/Requester.py:853: BadCredentialsException

During handling of the above exception, another exception occurred:

self = <tests.test_auth.TestAuthenticationGitHubIntegration object at 0x10a853050>
mock_github_class = <MagicMock name='Github' id='4476987024'>

    @patch("ticket_master_consolidated.Github")
    def test_create_client_token_parameter_overrides_instance(
        self, mock_github_class
    ):
        """Test that token parameter overrides instance token."""
        mock_github = MagicMock()
        mock_user = MagicMock()
        mock_user.login = "test_user"
        mock_github.get_user.return_value = mock_user
        mock_github_class.return_value = mock_github
    
        auth = Authentication("instance_token")
>       client = auth.create_client("override_token")
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_auth.py:118: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = Authentication(token_set=True, env_token_set=False, has_token=True)
token = 'override_token'

    def create_client(self, token: Optional[str] = None) -> Github:
        """Create authenticated GitHub client."""
        auth_token = token or self.get_token()
    
        try:
            auth = Auth.Token(auth_token)
            github_client = Github(auth=auth)
    
            # Test authentication by getting user info
            user = github_client.get_user()
            self.logger.info(f"Authenticated as GitHub user: {user.login}")
    
            return github_client
    
        except BadCredentialsException as e:
>           raise GitHubAuthError(f"Invalid GitHub credentials: {e}")
E           src.ticket_master_consolidated.GitHubAuthError: Invalid GitHub credentials: 401 {"message": "Bad credentials", "documentation_url": "https://docs.github.com/rest", "status": "401"}

src/ticket_master_consolidated.py:288: GitHubAuthError
______ TestAuthenticationGitHubIntegration.test_is_authenticated_success _______

self = <tests.test_auth.TestAuthenticationGitHubIntegration object at 0x10a853470>
mock_github_class = <MagicMock name='Github' id='4476650368'>

    @patch("ticket_master_consolidated.Github")
    def test_is_authenticated_success(self, mock_github_class):
        """Test is_authenticated with valid credentials."""
        mock_github = MagicMock()
        mock_user = MagicMock()
        mock_user.login = "test_user"
        mock_github.get_user.return_value = mock_user
        mock_github_class.return_value = mock_github
    
        auth = Authentication("valid_token")
        result = auth.is_authenticated()
    
>       assert result is True
E       assert False is True

tests/test_auth.py:161: AssertionError
____________ TestAuthenticationGitHubIntegration.test_get_user_info ____________

self = Authentication(token_set=True, env_token_set=False, has_token=True)
token = None

    def create_client(self, token: Optional[str] = None) -> Github:
        """Create authenticated GitHub client."""
        auth_token = token or self.get_token()
    
        try:
            auth = Auth.Token(auth_token)
            github_client = Github(auth=auth)
    
            # Test authentication by getting user info
            user = github_client.get_user()
>           self.logger.info(f"Authenticated as GitHub user: {user.login}")
                                                              ^^^^^^^^^^

src/ticket_master_consolidated.py:283: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
.venv/lib/python3.12/site-packages/github/AuthenticatedUser.py:294: in login
    self._completeIfNotSet(self._login)
.venv/lib/python3.12/site-packages/github/GithubObject.py:606: in _completeIfNotSet
    self._completeIfNeeded()
.venv/lib/python3.12/site-packages/github/GithubObject.py:610: in _completeIfNeeded
    self.__complete()
.venv/lib/python3.12/site-packages/github/GithubObject.py:615: in __complete
    headers, data = self._requester.requestJsonAndCheck("GET", self._url.value, headers=self.__completeHeaders)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.venv/lib/python3.12/site-packages/github/Requester.py:623: in requestJsonAndCheck
    return self.__check(
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <github.Requester.Requester object at 0x10ac0cbc0>, status = 401
responseHeaders = {'access-control-allow-origin': '*', 'access-control-expose-headers': 'ETag, Link, Location, Retry-After, X-GitHub-OTP...X-GitHub-Request-Id, Deprecation, Sunset', 'connection': 'close', 'content-security-policy': "default-src 'none'", ...}
output = '{\r\n  "message": "Bad credentials",\r\n  "documentation_url": "https://docs.github.com/rest",\r\n  "status": "401"\r\n}'

    def __check(
        self,
        status: int,
        responseHeaders: dict[str, Any],
        output: str,
    ) -> tuple[dict[str, Any], Any]:
        data = self.__structuredFromJson(output)
        if status >= 400:
>           raise self.createException(status, responseHeaders, data)
E           github.GithubException.BadCredentialsException: 401 {"message": "Bad credentials", "documentation_url": "https://docs.github.com/rest", "status": "401"}

.venv/lib/python3.12/site-packages/github/Requester.py:853: BadCredentialsException

During handling of the above exception, another exception occurred:

self = Authentication(token_set=True, env_token_set=False, has_token=True)

    def get_user_info(self) -> Dict[str, Any]:
        """Get detailed user information from GitHub."""
        try:
>           client = self.create_client()
                     ^^^^^^^^^^^^^^^^^^^^

src/ticket_master_consolidated.py:356: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = Authentication(token_set=True, env_token_set=False, has_token=True)
token = None

    def create_client(self, token: Optional[str] = None) -> Github:
        """Create authenticated GitHub client."""
        auth_token = token or self.get_token()
    
        try:
            auth = Auth.Token(auth_token)
            github_client = Github(auth=auth)
    
            # Test authentication by getting user info
            user = github_client.get_user()
            self.logger.info(f"Authenticated as GitHub user: {user.login}")
    
            return github_client
    
        except BadCredentialsException as e:
>           raise GitHubAuthError(f"Invalid GitHub credentials: {e}")
E           src.ticket_master_consolidated.GitHubAuthError: Invalid GitHub credentials: 401 {"message": "Bad credentials", "documentation_url": "https://docs.github.com/rest", "status": "401"}

src/ticket_master_consolidated.py:288: GitHubAuthError

During handling of the above exception, another exception occurred:

self = <tests.test_auth.TestAuthenticationGitHubIntegration object at 0x10a853710>
mock_github_class = <MagicMock name='Github' id='4476525632'>

    @patch("ticket_master_consolidated.Github")
    def test_get_user_info(self, mock_github_class):
        """Test getting user information."""
        mock_github = MagicMock()
        mock_user = MagicMock()
    
        mock_user.login = "test_user"
        mock_user.name = "Test User"
        mock_user.email = "test@example.com"
        mock_user.public_repos = 10
        mock_user.followers = 5
        mock_user.following = 3
        mock_user.created_at.isoformat.return_value = "2020-01-01T00:00:00"
        mock_user.updated_at.isoformat.return_value = "2023-01-01T00:00:00"
    
        mock_github.get_user.return_value = mock_user
        mock_github_class.return_value = mock_github
    
        auth = Authentication("valid_token")
>       user_info = auth.get_user_info()
                    ^^^^^^^^^^^^^^^^^^^^

tests/test_auth.py:198: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = Authentication(token_set=True, env_token_set=False, has_token=True)

    def get_user_info(self) -> Dict[str, Any]:
        """Get detailed user information from GitHub."""
        try:
            client = self.create_client()
            user = client.get_user()
    
            return {
                "login": user.login,
                "name": user.name,
                "email": user.email,
                "public_repos": user.public_repos,
                "followers": user.followers,
                "following": user.following,
                "created_at": (
                    user.created_at.isoformat() if user.created_at else None
                ),
                "updated_at": (
                    user.updated_at.isoformat() if user.updated_at else None
                ),
            }
        except Exception as e:
>           raise GitHubAuthError(f"Failed to get user info: {e}")
E           src.ticket_master_consolidated.GitHubAuthError: Failed to get user info: Invalid GitHub credentials: 401 {"message": "Bad credentials", "documentation_url": "https://docs.github.com/rest", "status": "401"}

src/ticket_master_consolidated.py:374: GitHubAuthError
_______ TestAuthenticationGitHubIntegration.test_test_connection_success _______

self = <tests.test_auth.TestAuthenticationGitHubIntegration object at 0x10a853860>
mock_github_class = <MagicMock name='Github' id='4475987888'>

    @patch("ticket_master_consolidated.Github")
    def test_test_connection_success(self, mock_github_class):
        """Test successful connection test."""
        mock_github = MagicMock()
        mock_user = MagicMock()
        mock_rate_limit = MagicMock()
        mock_core = MagicMock()
    
        mock_user.login = "test_user"
        mock_user.name = "Test User"
        mock_user.email = "test@example.com"
        mock_user.public_repos = 10
        mock_user.followers = 5
    
        mock_core.limit = 5000
        mock_core.remaining = 4999
        mock_core.reset.isoformat.return_value = "2023-01-01T01:00:00"
        mock_rate_limit.core = mock_core
    
        mock_github.get_user.return_value = mock_user
        mock_github.get_rate_limit.return_value = mock_rate_limit
        mock_github_class.return_value = mock_github
    
        auth = Authentication("valid_token")
        result = auth.test_connection()
    
>       assert result["authenticated"] is True
E       assert False is True

tests/test_auth.py:239: AssertionError
______ TestAuthenticationErrorHandling.test_github_auth_error_inheritance ______

self = <tests.test_auth.TestAuthenticationErrorHandling object at 0x10a853d10>

    def test_github_auth_error_inheritance(self):
        """Test that GitHubAuthError inherits from AuthenticationError."""
        error = GitHubAuthError("auth error")
>       assert isinstance(error, AuthenticationError)
E       AssertionError: assert False
E        +  where False = isinstance(GitHubAuthError('auth error'), AuthenticationError)

tests/test_auth.py:273: AssertionError
____________ TestSupportsColor.test_supports_color_force_color_env _____________

self = <tests.test_colors.TestSupportsColor object at 0x10a8ac4a0>
mock_stdout = <MagicMock name='stdout' id='4475935424'>

    @patch("sys.stdout")
    @patch.dict(os.environ, {"FORCE_COLOR": "1", "TERM": "dumb"})
    def test_supports_color_force_color_env(self, mock_stdout):
        """Test that FORCE_COLOR environment variable enables colors."""
        mock_stdout.isatty.return_value = True
>       assert supports_color() is True
E       assert False is True
E        +  where False = supports_color()

tests/test_colors.py:150: AssertionError
________________ TestColorize.test_colorize_with_colors_enabled ________________

self = <tests.test_colors.TestColorize object at 0x10a8acdd0>

    def test_colorize_with_colors_enabled(self):
        """Test colorize function when colors are enabled."""
        enable_colors(True)
        result = colorize("test", Colors.RED, Colors.BOLD)
        expected = f"{Colors.BOLD}{Colors.RED}test{Colors.RESET}"
>       assert result == expected
E       AssertionError: assert '\x1b[91m\x1b[1mtest\x1b[0m' == '\x1b[1m\x1b[91mtest\x1b[0m'
E         
E         - [1m[91mtest[0m
E         ?       -
E         + [91m[1mtest[0m
E         ?   +

tests/test_colors.py:195: AssertionError
____________________ TestColorize.test_colorize_only_style _____________________

self = <tests.test_colors.TestColorize object at 0x10a88bce0>

    def test_colorize_only_style(self):
        """Test colorize function with only style."""
        enable_colors(True)
>       result = colorize("test", style=Colors.ITALIC)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: colorize() got an unexpected keyword argument 'style'

tests/test_colors.py:213: TypeError
______________ TestFormattingFunctions.test_success_function_bold ______________

self = <tests.test_colors.TestFormattingFunctions object at 0x10a8acef0>

    def test_success_function_bold(self):
        """Test success formatting function with bold."""
        enable_colors(True)
        result = success("test message", bold=True)
        expected = f"{Colors.BOLD}{Colors.GREEN}test message{Colors.RESET}"
>       assert result == expected
E       AssertionError: assert '\x1b[92m\x1b...essage\x1b[0m' == '\x1b[1m\x1b[...essage\x1b[0m'
E         
E         - [1m[92mtest message[0m
E         ? ----
E         + [92m[1mtest message[0m
E         ?      ++++

tests/test_colors.py:244: AssertionError
_________________ TestFormattingFunctions.test_error_function __________________

self = <tests.test_colors.TestFormattingFunctions object at 0x10a8ac980>

    def test_error_function(self):
        """Test error formatting function."""
        enable_colors(True)
        result = error("test message")
        expected = f"{Colors.RED}test message{Colors.RESET}"
>       assert result == expected
E       AssertionError: assert '\x1b[91m\x1b...essage\x1b[0m' == '\x1b[91mtest message\x1b[0m'
E         
E         - [91mtest message[0m
E         + [91m[1mtest message[0m
E         ?    ++++

tests/test_colors.py:251: AssertionError
_______________ TestFormattingFunctions.test_error_function_bold _______________

self = <tests.test_colors.TestFormattingFunctions object at 0x10a8ac740>

    def test_error_function_bold(self):
        """Test error formatting function with bold."""
        enable_colors(True)
        result = error("test message", bold=True)
        expected = f"{Colors.BOLD}{Colors.RED}test message{Colors.RESET}"
>       assert result == expected
E       AssertionError: assert '\x1b[91m\x1b...essage\x1b[0m' == '\x1b[1m\x1b[...essage\x1b[0m'
E         
E         - [1m[91mtest message[0m
E         ?       -
E         + [91m[1mtest message[0m
E         ?   +

tests/test_colors.py:258: AssertionError
______________ TestFormattingFunctions.test_warning_function_bold ______________

self = <tests.test_colors.TestFormattingFunctions object at 0x10a8ad250>

    def test_warning_function_bold(self):
        """Test warning formatting function with bold."""
        enable_colors(True)
        result = warning("test message", bold=True)
        expected = f"{Colors.BOLD}{Colors.YELLOW}test message{Colors.RESET}"
>       assert result == expected
E       AssertionError: assert '\x1b[93m\x1b...essage\x1b[0m' == '\x1b[1m\x1b[...essage\x1b[0m'
E         
E         - [1m[93mtest message[0m
E         ? ----
E         + [93m[1mtest message[0m
E         ?      ++++

tests/test_colors.py:272: AssertionError
_______________ TestFormattingFunctions.test_info_function_bold ________________

self = <tests.test_colors.TestFormattingFunctions object at 0x10a8ad550>

    def test_info_function_bold(self):
        """Test info formatting function with bold."""
        enable_colors(True)
        result = info("test message", bold=True)
        expected = f"{Colors.BOLD}{Colors.BLUE}test message{Colors.RESET}"
>       assert result == expected
E       AssertionError: assert '\x1b[94m\x1b...essage\x1b[0m' == '\x1b[1m\x1b[...essage\x1b[0m'
E         
E         - [1m[94mtest message[0m
E         ? ----
E         + [94m[1mtest message[0m
E         ?      ++++

tests/test_colors.py:286: AssertionError
_____________ TestFormattingFunctions.test_header_function_default _____________

self = <tests.test_colors.TestFormattingFunctions object at 0x10a8ad6d0>

    def test_header_function_default(self):
        """Test header formatting function with default color."""
        enable_colors(True)
        result = header("test message")
        expected = f"{Colors.BOLD}{Colors.CYAN}test message{Colors.RESET}"
>       assert result == expected
E       AssertionError: assert '\x1b[96m\x1b...essage\x1b[0m' == '\x1b[1m\x1b[...essage\x1b[0m'
E         
E         - [1m[96mtest message[0m
E         ? ----
E         + [96m[1mtest message[0m
E         ?      ++++

tests/test_colors.py:293: AssertionError
__________ TestFormattingFunctions.test_header_function_custom_color ___________

self = <tests.test_colors.TestFormattingFunctions object at 0x10a8ad850>

    def test_header_function_custom_color(self):
        """Test header formatting function with custom color."""
        enable_colors(True)
>       result = header("test message", Colors.MAGENTA)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: header() takes 1 positional argument but 2 were given

tests/test_colors.py:298: TypeError
___________ TestFormattingFunctions.test_highlight_function_default ____________

self = <tests.test_colors.TestFormattingFunctions object at 0x10a8ad9d0>

    def test_highlight_function_default(self):
        """Test highlight formatting function with default color."""
        enable_colors(True)
        result = highlight("test message")
        expected = f"{Colors.MAGENTA}test message{Colors.RESET}"
>       assert result == expected
E       AssertionError: assert '\x1b[97m\x1b...essage\x1b[0m' == '\x1b[95mtest message\x1b[0m'
E         
E         - [95mtest message[0m
E         ?    ^
E         + [97m[1mtest message[0m
E         ?    ^^^^^

tests/test_colors.py:307: AssertionError
_________ TestFormattingFunctions.test_highlight_function_custom_color _________

self = <tests.test_colors.TestFormattingFunctions object at 0x10a8adb50>

    def test_highlight_function_custom_color(self):
        """Test highlight formatting function with custom color."""
        enable_colors(True)
>       result = highlight("test message", Colors.YELLOW)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: highlight() takes 1 positional argument but 2 were given

tests/test_colors.py:312: TypeError
_________________ TestProgressBar.test_progress_bar_zero_total _________________

self = <tests.test_colors.TestProgressBar object at 0x10a8ade80>

    def test_progress_bar_zero_total(self):
        """Test progress bar with zero total."""
        enable_colors(True)
        result = progress_bar(0, 0, width=10)
        expected = "[          ] 0%"
>       assert result == expected
E       AssertionError: assert ' \x1b[92m███...\x1b[0m 100% ' == '[          ] 0%'
E         
E         - [          ] 0%
E         +  [92m██████████[0m[90m[0m 100%

tests/test_colors.py:332: AssertionError
______________ TestProgressBar.test_progress_bar_full_completion _______________

self = <tests.test_colors.TestProgressBar object at 0x10a8ae000>

    def test_progress_bar_full_completion(self):
        """Test progress bar at full completion."""
        enable_colors(True)
        result = progress_bar(10, 10, width=10)
        expected = f"[{Colors.GREEN}██████████{Colors.RESET}] 100.0%"
>       assert result == expected
E       AssertionError: assert ' \x1b[92m███...\x1b[0m 100% ' == '[\x1b[92m███...1b[0m] 100.0%'
E         
E         - [[92m██████████[0m] 100.0%
E         ? ^                   ^    --
E         +  [92m██████████[0m[90m[0m 100% 
E         ? ^                   ^^^^^^^^^     +

tests/test_colors.py:339: AssertionError
______________ TestProgressBar.test_progress_bar_half_completion _______________

self = <tests.test_colors.TestProgressBar object at 0x10a8ae180>

    def test_progress_bar_half_completion(self):
        """Test progress bar at half completion."""
        enable_colors(True)
        result = progress_bar(5, 10, width=10)
        expected = f"[{Colors.GREEN}█████{Colors.RESET}░░░░░] 50.0%"
>       assert result == expected
E       AssertionError: assert ' \x1b[92m███...░\x1b[0m 50% ' == '[\x1b[92m███...m░░░░░] 50.0%'
E         
E         - [[92m█████[0m░░░░░] 50.0%
E         ? ^                   ^   --
E         +  [92m█████[0m[90m░░░░░[0m 50% 
E         ? ^              +++++     ^^^^    +

tests/test_colors.py:346: AssertionError
________________ TestProgressBar.test_progress_bar_custom_color ________________

self = <tests.test_colors.TestProgressBar object at 0x10a8ae300>

    def test_progress_bar_custom_color(self):
        """Test progress bar with custom color."""
        enable_colors(True)
>       result = progress_bar(3, 10, width=10, color=Colors.BLUE)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: progress_bar() got an unexpected keyword argument 'color'

tests/test_colors.py:351: TypeError
________________ TestProgressBar.test_progress_bar_custom_width ________________

self = <tests.test_colors.TestProgressBar object at 0x10a8ae480>

    def test_progress_bar_custom_width(self):
        """Test progress bar with custom width."""
        enable_colors(True)
        result = progress_bar(1, 4, width=8)
        expected = f"[{Colors.GREEN}██{Colors.RESET}░░░░░░] 25.0%"
>       assert result == expected
E       AssertionError: assert ' \x1b[92m██\...░\x1b[0m 25% ' == '[\x1b[92m██\...░░░░░░] 25.0%'
E         
E         - [[92m██[0m░░░░░░] 25.0%
E         +  [92m██[0m[90m░░░░░░[0m 25%

tests/test_colors.py:360: AssertionError
______________ TestProgressBar.test_progress_bar_colors_disabled _______________

self = <tests.test_colors.TestProgressBar object at 0x10a8ae600>

    def test_progress_bar_colors_disabled(self):
        """Test progress bar when colors are disabled."""
        enable_colors(False)
        result = progress_bar(5, 10, width=10)
        expected = "[█████░░░░░] 50.0%"
>       assert result == expected
E       AssertionError: assert ' █████░░░░░ 50% ' == '[█████░░░░░] 50.0%'
E         
E         - [█████░░░░░] 50.0%
E         ? ^          -   --
E         +  █████░░░░░ 50% 
E         ? ^              +

tests/test_colors.py:367: AssertionError
__________________ TestPrintColored.test_print_colored_basic ___________________

self = <tests.test_colors.TestPrintColored object at 0x10a8ae7b0>
mock_print = <MagicMock name='print' id='4476531968'>

    @patch("builtins.print")
    def test_print_colored_basic(self, mock_print):
        """Test print_colored function basic usage."""
        enable_colors(True)
        print_colored("test message", Colors.RED, Colors.BOLD)
        expected = f"{Colors.BOLD}{Colors.RED}test message{Colors.RESET}"
>       mock_print.assert_called_once_with(expected)

tests/test_colors.py:379: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:961: in assert_called_once_with
    return self.assert_called_with(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <MagicMock name='print' id='4476531968'>
args = ('\x1b[1m\x1b[91mtest message\x1b[0m',), kwargs = {}
expected = call('\x1b[1m\x1b[91mtest message\x1b[0m')
actual = call('\x1b[91m\x1b[1mtest message\x1b[0m')
_error_message = <function NonCallableMock.assert_called_with.<locals>._error_message at 0x10ad522a0>
cause = None

    def assert_called_with(self, /, *args, **kwargs):
        """assert that the last call was made with the specified arguments.
    
        Raises an AssertionError if the args and keyword args passed in are
        different to the last call to the mock."""
        if self.call_args is None:
            expected = self._format_mock_call_signature(args, kwargs)
            actual = 'not called.'
            error_message = ('expected call not found.\nExpected: %s\n  Actual: %s'
                    % (expected, actual))
            raise AssertionError(error_message)
    
        def _error_message():
            msg = self._format_mock_failure_message(args, kwargs)
            return msg
        expected = self._call_matcher(_Call((args, kwargs), two=True))
        actual = self._call_matcher(self.call_args)
        if actual != expected:
            cause = expected if isinstance(expected, Exception) else None
>           raise AssertionError(_error_message()) from cause
E           AssertionError: expected call not found.
E           Expected: print('\x1b[1m\x1b[91mtest message\x1b[0m')
E             Actual: print('\x1b[91m\x1b[1mtest message\x1b[0m')

/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:949: AssertionError
_ TestFormattingFunctionsColorsDisabled.test_all_formatting_functions_colors_disabled _

self = <tests.test_colors.TestFormattingFunctionsColorsDisabled object at 0x10a8ae420>

    def test_all_formatting_functions_colors_disabled(self):
        """Test that all formatting functions return plain text when colors are disabled."""
        enable_colors(False)
    
        test_text = "test message"
    
        assert success(test_text) == test_text
        assert success(test_text, bold=True) == test_text
        assert error(test_text) == test_text
        assert error(test_text, bold=True) == test_text
        assert warning(test_text) == test_text
        assert warning(test_text, bold=True) == test_text
        assert info(test_text) == test_text
        assert info(test_text, bold=True) == test_text
        assert header(test_text) == test_text
>       assert header(test_text, Colors.RED) == test_text
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: header() takes 1 positional argument but 2 were given

tests/test_colors.py:423: TypeError
__________________ TestEdgeCases.test_empty_string_formatting __________________

self = <tests.test_colors.TestEdgeCases object at 0x10a8adfa0>

    def test_empty_string_formatting(self):
        """Test formatting functions with empty strings."""
        enable_colors(True)
    
        assert success("") == f"{Colors.GREEN}{Colors.RESET}"
>       assert error("") == f"{Colors.RED}{Colors.RESET}"
E       AssertionError: assert '\x1b[91m\x1b[1m\x1b[0m' == '\x1b[91m\x1b[0m'
E         
E         - [91m[0m
E         + [91m[1m[0m
E         ?        ++++

tests/test_colors.py:437: AssertionError
__________________ TestEdgeCases.test_progress_bar_edge_cases __________________

self = <tests.test_colors.TestEdgeCases object at 0x10a8ad370>

    def test_progress_bar_edge_cases(self):
        """Test progress bar with edge cases."""
        enable_colors(True)
    
        # Test with completed > total
        result = progress_bar(15, 10, width=10)
        expected = f"[{Colors.GREEN}██████████{Colors.RESET}] 150.0%"
>       assert result == expected
E       AssertionError: assert ' \x1b[92m███...\x1b[0m 100% ' == '[\x1b[92m███...1b[0m] 150.0%'
E         
E         - [[92m██████████[0m] 150.0%
E         ? ^                   ^  - -
E         +  [92m██████████[0m[90m[0m 100% 
E         ? ^                   ^^^^^^^^^     +

tests/test_colors.py:466: AssertionError
_____________________ TestCommit.test_init_invalid_commit ______________________

self = <tests.test_commit.TestCommit testMethod=test_init_invalid_commit>

    def test_init_invalid_commit(self):
        """Test Commit initialization with invalid commit object."""
        with self.assertRaises(CommitError):
>           Commit(None)

tests/test_commit.py:74: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

    def __init__(self, commit_data) -> None:
        """Initialize Commit from git commit object or commit data dictionary."""
        if hasattr(commit_data, "hexsha"):
            # Git commit object
            self.git_commit = commit_data
            self.hash = commit_data.hexsha
            self.short_hash = commit_data.hexsha[:8]
    
            # Author info
            self.author = {
                "name": getattr(commit_data.author, "name", "Unknown"),
                "email": getattr(
                    commit_data.author, "email", "unknown@example.com"
                ),
            }
    
            # Committer info
            self.committer = {
                "name": getattr(commit_data.committer, "name", "Unknown"),
                "email": getattr(
                    commit_data.committer, "email", "unknown@example.com"
                ),
            }
    
            self.message = getattr(commit_data, "message", "")
            self.summary = getattr(
                commit_data, "summary", self.message.split("\n")[0]
            )
    
            # Date handling
            if hasattr(commit_data, "committed_datetime"):
                self.date = commit_data.committed_datetime
            elif hasattr(commit_data, "committed_date"):
                from datetime import datetime
    
                self.date = datetime.fromtimestamp(commit_data.committed_date)
            else:
                self.date = datetime.now()
    
            # Stats
            try:
                if hasattr(commit_data, "stats"):
                    stats = commit_data.stats
                    if hasattr(stats, "total"):
                        self.insertions = stats.total.get("insertions", 0)
                        self.deletions = stats.total.get("deletions", 0)
                        self.files_changed = len(getattr(stats, "files", {}))
                    else:
                        self.insertions = 0
                        self.deletions = 0
                        self.files_changed = 0
                else:
                    self.insertions = 0
                    self.deletions = 0
                    self.files_changed = 0
            except:
                self.insertions = 0
                self.deletions = 0
                self.files_changed = 0
    
        else:
            # Dictionary data (legacy compatibility)
            self.git_commit = None
>           self.hash = commit_data.get("hash", "")
                        ^^^^^^^^^^^^^^^
E           AttributeError: 'NoneType' object has no attribute 'get'

src/ticket_master_consolidated.py:493: AttributeError
________________ TestDataScraper.test_analyze_activity_patterns ________________

self = <tests.test_data_scraper.TestDataScraper testMethod=test_analyze_activity_patterns>

    def test_analyze_activity_patterns(self):
        """Test activity pattern analysis."""
        # Mock the git operations to avoid repository-specific issues
        with (
>           patch.object(
                self.scraper, "_analyze_commit_frequency"
            ) as mock_freq,
            patch.object(self.scraper, "_analyze_time_patterns") as mock_time,
            patch.object(
                self.scraper, "_analyze_file_hotspots"
            ) as mock_hotspots,
            patch.object(
                self.scraper, "_analyze_contributor_activity"
            ) as mock_activity,
        ):

tests/test_data_scraper.py:219: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1467: in __enter__
    original, local = self.get_original()
                      ^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <unittest.mock._patch object at 0x10ac94e00>

    def get_original(self):
        target = self.getter()
        name = self.attribute
    
        original = DEFAULT
        local = False
    
        try:
            original = target.__dict__[name]
        except (AttributeError, KeyError):
            original = getattr(target, name, DEFAULT)
        else:
            local = True
    
        if name in _builtins and isinstance(target, ModuleType):
            self.create = True
    
        if not self.create and original is DEFAULT:
>           raise AttributeError(
                "%s does not have the attribute %r" % (target, name)
            )
E           AttributeError: <src.ticket_master_consolidated.DataScraper object at 0x10a8af440> does not have the attribute '_analyze_commit_frequency'

/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1437: AttributeError
__________________ TestDataScraper.test_analyze_code_quality ___________________

self = <tests.test_data_scraper.TestDataScraper testMethod=test_analyze_code_quality>

    def test_analyze_code_quality(self):
        """Test code quality analysis."""
>       quality = self.scraper.analyze_code_quality()
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: 'DataScraper' object has no attribute 'analyze_code_quality'

tests/test_data_scraper.py:208: AttributeError
______________ TestDataScraper.test_init_invalid_repository_error ______________

self = <tests.test_data_scraper.TestDataScraper testMethod=test_init_invalid_repository_error>

    def test_init_invalid_repository_error(self):
        """Test initialization with repository that exists but is invalid."""
>       from repository import RepositoryError
E       ModuleNotFoundError: No module named 'repository'

tests/test_data_scraper.py:66: ModuleNotFoundError
_________________ TestDataScraper.test_init_with_cache_enabled _________________

self = <tests.test_data_scraper.TestDataScraper testMethod=test_init_with_cache_enabled>

    def test_init_with_cache_enabled(self):
        """Test DataScraper initialization with caching enabled."""
>       with patch("data_scraper.UserDatabase") as mock_db:
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_data_scraper.py:41: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1451: in __enter__
    self.target = self.getter()
                  ^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pkgutil.py:513: in resolve_name
    mod = importlib.import_module(modname)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:1387: in _gcd_import
    ???
<frozen importlib._bootstrap>:1360: in _find_and_load
    ???
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

name = 'data_scraper', import_ = <function _gcd_import at 0x1022ec0e0>

>   ???
E   ModuleNotFoundError: No module named 'data_scraper'

<frozen importlib._bootstrap>:1324: ModuleNotFoundError
_________________ TestDataScraper.test_init_with_cache_failure _________________

self = <tests.test_data_scraper.TestDataScraper testMethod=test_init_with_cache_failure>

    def test_init_with_cache_failure(self):
        """Test DataScraper initialization with cache database failure."""
>       from database import DatabaseError
E       ModuleNotFoundError: No module named 'database'

tests/test_data_scraper.py:53: ModuleNotFoundError
_______________________ TestDataScraper.test_scrape_all ________________________

self = <tests.test_data_scraper.TestDataScraper testMethod=test_scrape_all>

    def test_scrape_all(self):
        """Test comprehensive scraping of all repository data."""
        with (
>           patch.object(
                self.scraper, "scrape_repository_info"
            ) as mock_repo_info,
            patch.object(self.scraper, "scrape_git_history") as mock_git,
            patch.object(self.scraper, "scrape_file_structure") as mock_files,
            patch.object(
                self.scraper, "scrape_content_analysis"
            ) as mock_content,
            patch.object(self.scraper, "scrape_dependencies") as mock_deps,
            patch.object(
                self.scraper, "scrape_build_configuration"
            ) as mock_build,
            patch.object(self.scraper, "analyze_code_quality") as mock_quality,
            patch.object(
                self.scraper, "analyze_activity_patterns"
            ) as mock_activity,
        ):

tests/test_data_scraper.py:106: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1467: in __enter__
    original, local = self.get_original()
                      ^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <unittest.mock._patch object at 0x10ad12870>

    def get_original(self):
        target = self.getter()
        name = self.attribute
    
        original = DEFAULT
        local = False
    
        try:
            original = target.__dict__[name]
        except (AttributeError, KeyError):
            original = getattr(target, name, DEFAULT)
        else:
            local = True
    
        if name in _builtins and isinstance(target, ModuleType):
            self.create = True
    
        if not self.create and original is DEFAULT:
>           raise AttributeError(
                "%s does not have the attribute %r" % (target, name)
            )
E           AttributeError: <src.ticket_master_consolidated.DataScraper object at 0x10ac94dd0> does not have the attribute 'scrape_repository_info'

/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1437: AttributeError
_______________ TestDataScraper.test_scrape_build_configuration ________________

self = <tests.test_data_scraper.TestDataScraper testMethod=test_scrape_build_configuration>

    def test_scrape_build_configuration(self):
        """Test build configuration analysis."""
>       build_config = self.scraper.scrape_build_configuration()
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: 'DataScraper' object has no attribute 'scrape_build_configuration'

tests/test_data_scraper.py:200: AttributeError
_________________ TestDataScraper.test_scrape_content_analysis _________________

self = <tests.test_data_scraper.TestDataScraper testMethod=test_scrape_content_analysis>

    def test_scrape_content_analysis(self):
        """Test content analysis."""
>       analysis = self.scraper.scrape_content_analysis()
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: 'DataScraper' object has no attribute 'scrape_content_analysis'

tests/test_data_scraper.py:95: AttributeError
___________________ TestDataScraper.test_scrape_dependencies ___________________

self = <tests.test_data_scraper.TestDataScraper testMethod=test_scrape_dependencies>

    def test_scrape_dependencies(self):
        """Test dependency analysis."""
>       deps = self.scraper.scrape_dependencies()
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: 'DataScraper' object has no attribute 'scrape_dependencies'

tests/test_data_scraper.py:189: AttributeError
__________________ TestDataScraper.test_scrape_file_structure __________________

self = <tests.test_data_scraper.TestDataScraper testMethod=test_scrape_file_structure>

    def test_scrape_file_structure(self):
        """Test file structure analysis."""
>       structure = self.scraper.scrape_file_structure()
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: 'DataScraper' object has no attribute 'scrape_file_structure'

tests/test_data_scraper.py:86: AttributeError
___________________ TestDataScraper.test_scrape_git_history ____________________

self = <tests.test_data_scraper.TestDataScraper testMethod=test_scrape_git_history>

    def test_scrape_git_history(self):
        """Test Git history scraping."""
        # Mock successful git history to avoid repository-specific issues
        with (
>           patch.object(self.scraper, "_analyze_commits") as mock_commits,
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            patch.object(
                self.scraper, "_analyze_contributors"
            ) as mock_contributors,
            patch.object(self.scraper, "_analyze_branches") as mock_branches,
        ):

tests/test_data_scraper.py:159: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1467: in __enter__
    original, local = self.get_original()
                      ^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <unittest.mock._patch object at 0x10ac3fb60>

    def get_original(self):
        target = self.getter()
        name = self.attribute
    
        original = DEFAULT
        local = False
    
        try:
            original = target.__dict__[name]
        except (AttributeError, KeyError):
            original = getattr(target, name, DEFAULT)
        else:
            local = True
    
        if name in _builtins and isinstance(target, ModuleType):
            self.create = True
    
        if not self.create and original is DEFAULT:
>           raise AttributeError(
                "%s does not have the attribute %r" % (target, name)
            )
E           AttributeError: <src.ticket_master_consolidated.DataScraper object at 0x10ad471d0> does not have the attribute '_analyze_commits'

/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1437: AttributeError
_________________ TestDataScraper.test_scrape_repository_info __________________

self = <tests.test_data_scraper.TestDataScraper testMethod=test_scrape_repository_info>

    def test_scrape_repository_info(self):
        """Test repository information scraping."""
>       info = self.scraper.scrape_repository_info()
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: 'DataScraper' object has no attribute 'scrape_repository_info'

tests/test_data_scraper.py:78: AttributeError
____________ TestDataScraperCaching.test_get_from_cache_no_cache_db ____________

self = <tests.test_data_scraper.TestDataScraperCaching testMethod=test_get_from_cache_no_cache_db>

    def test_get_from_cache_no_cache_db(self):
        """Test cache retrieval when no cache database is available."""
        scraper = DataScraper(self.repo_path, use_cache=False)
>       result = scraper._get_from_cache("test_key")
                 ^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: 'DataScraper' object has no attribute '_get_from_cache'

tests/test_data_scraper.py:253: AttributeError
______________ TestDataScraperCaching.test_get_from_cache_with_db ______________

self = <tests.test_data_scraper.TestDataScraperCaching testMethod=test_get_from_cache_with_db>
mock_db = <MagicMock name='UserDatabase' id='4476452064'>

    @patch("ticket_master_consolidated.UserDatabase")
    def test_get_from_cache_with_db(self, mock_db):
        """Test cache retrieval with database."""
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
    
        scraper = DataScraper(self.repo_path, use_cache=True)
    
        # Just verify that get method is called, not specific return value
>       result = scraper._get_from_cache("test_key")
                 ^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: 'DataScraper' object has no attribute '_get_from_cache'

tests/test_data_scraper.py:265: AttributeError
------------------------------ Captured log call -------------------------------
WARNING  DataScraper:ticket_master_consolidated.py:1950 Cache DB error: 'UserDatabase' object has no attribute 'create_tables'
____________ TestDataScraperCaching.test_store_in_cache_no_cache_db ____________

self = <tests.test_data_scraper.TestDataScraperCaching testMethod=test_store_in_cache_no_cache_db>

    def test_store_in_cache_no_cache_db(self):
        """Test cache storage when no cache database is available."""
        scraper = DataScraper(self.repo_path, use_cache=False)
        # Should not raise exception
>       scraper._store_in_cache("test_key", {"test": "data"})
        ^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: 'DataScraper' object has no attribute '_store_in_cache'

tests/test_data_scraper.py:286: AttributeError
______________ TestDataScraperCaching.test_store_in_cache_with_db ______________

self = <tests.test_data_scraper.TestDataScraperCaching testMethod=test_store_in_cache_with_db>
mock_db = <MagicMock name='UserDatabase' id='4475570416'>

    @patch("ticket_master_consolidated.UserDatabase")
    def test_store_in_cache_with_db(self, mock_db):
        """Test cache storage with database."""
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
    
        scraper = DataScraper(self.repo_path, use_cache=True)
>       scraper._store_in_cache("test_key", {"test": "data"})
        ^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: 'DataScraper' object has no attribute '_store_in_cache'

tests/test_data_scraper.py:277: AttributeError
------------------------------ Captured log call -------------------------------
WARNING  DataScraper:ticket_master_consolidated.py:1950 Cache DB error: 'UserDatabase' object has no attribute 'create_tables'
_____________ TestDataScraperPrivateMethods.test_analyze_branches ______________

self = <tests.test_data_scraper.TestDataScraperPrivateMethods testMethod=test_analyze_branches>

    def test_analyze_branches(self):
        """Test branch analysis."""
>       branches = self.scraper._analyze_branches()
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: 'DataScraper' object has no attribute '_analyze_branches'

tests/test_data_scraper.py:392: AttributeError
______________ TestDataScraperPrivateMethods.test_analyze_commits ______________

self = <tests.test_data_scraper.TestDataScraperPrivateMethods testMethod=test_analyze_commits>

    def test_analyze_commits(self):
        """Test commit analysis."""
        # Mock some commits data
        mock_commits = [
            {
                "hash": "abc123",
                "message": "Initial commit",
                "author": "test@example.com",
                "date": "2023-01-01",
            },
            {
                "hash": "def456",
                "message": "Add feature",
                "author": "test@example.com",
                "date": "2023-01-02",
            },
        ]
    
>       with patch.object(
            self.scraper.repository, "get_commits"
        ) as mock_get_commits:

tests/test_data_scraper.py:356: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1467: in __enter__
    original, local = self.get_original()
                      ^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <unittest.mock._patch object at 0x10ac7eb40>

    def get_original(self):
        target = self.getter()
        name = self.attribute
    
        original = DEFAULT
        local = False
    
        try:
            original = target.__dict__[name]
        except (AttributeError, KeyError):
            original = getattr(target, name, DEFAULT)
        else:
            local = True
    
        if name in _builtins and isinstance(target, ModuleType):
            self.create = True
    
        if not self.create and original is DEFAULT:
>           raise AttributeError(
                "%s does not have the attribute %r" % (target, name)
            )
E           AttributeError: Repository(path='/Users/dhodgson/Desktop/Ticket-Master', branch='copilot/fix-e3614c64-21e3-4357-8b4f-571781a0aa64') does not have the attribute 'get_commits'

/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1437: AttributeError
___________ TestDataScraperPrivateMethods.test_analyze_contributors ____________

self = <tests.test_data_scraper.TestDataScraperPrivateMethods testMethod=test_analyze_contributors>

    def test_analyze_contributors(self):
        """Test contributor analysis."""
        mock_commits = [
            {"author": "alice@example.com", "date": "2023-01-01"},
            {"author": "bob@example.com", "date": "2023-01-02"},
            {"author": "alice@example.com", "date": "2023-01-03"},
        ]
    
>       result = self.scraper._analyze_contributors(mock_commits)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: 'DataScraper' object has no attribute '_analyze_contributors'

tests/test_data_scraper.py:375: AttributeError
_________ TestDataScraperPrivateMethods.test_calculate_repository_size _________

self = <tests.test_data_scraper.TestDataScraperPrivateMethods testMethod=test_calculate_repository_size>

    def test_calculate_repository_size(self):
        """Test repository size calculation."""
>       size_info = self.scraper._calculate_repository_size()
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: 'DataScraper' object has no attribute '_calculate_repository_size'

tests/test_data_scraper.py:298: AttributeError
____________ TestDataScraperPrivateMethods.test_extract_git_config _____________

self = <tests.test_data_scraper.TestDataScraperPrivateMethods testMethod=test_extract_git_config>

    def test_extract_git_config(self):
        """Test Git configuration extraction."""
>       config = self.scraper._extract_git_config()
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: 'DataScraper' object has no attribute '_extract_git_config'

tests/test_data_scraper.py:323: AttributeError
____________ TestDataScraperPrivateMethods.test_extract_remote_info ____________

self = <tests.test_data_scraper.TestDataScraperPrivateMethods testMethod=test_extract_remote_info>

    def test_extract_remote_info(self):
        """Test remote information extraction."""
>       remotes = self.scraper._extract_remote_info()
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: 'DataScraper' object has no attribute '_extract_remote_info'

tests/test_data_scraper.py:330: AttributeError
______ TestDataScraperPrivateMethods.test_scrape_repository_info_detailed ______
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1393: in patched
    with self.decoration_helper(patched,
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/contextlib.py:137: in __enter__
    return next(self.gen)
           ^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1375: in decoration_helper
    arg = exit_stack.enter_context(patching)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/contextlib.py:526: in enter_context
    result = _enter(cm)
             ^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1467: in __enter__
    original, local = self.get_original()
                      ^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <unittest.mock._patch object at 0x10a8adf70>

    def get_original(self):
        target = self.getter()
        name = self.attribute
    
        original = DEFAULT
        local = False
    
        try:
            original = target.__dict__[name]
        except (AttributeError, KeyError):
            original = getattr(target, name, DEFAULT)
        else:
            local = True
    
        if name in _builtins and isinstance(target, ModuleType):
            self.create = True
    
        if not self.create and original is DEFAULT:
>           raise AttributeError(
                "%s does not have the attribute %r" % (target, name)
            )
E           AttributeError: <class 'src.ticket_master_consolidated.DataScraper'> does not have the attribute '_extract_remote_info'

/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1437: AttributeError
________ TestDataScraperDependencyAnalysis.test_extract_go_dependencies ________

self = <tests.test_data_scraper.TestDataScraperDependencyAnalysis testMethod=test_extract_go_dependencies>

    def test_extract_go_dependencies(self):
        """Test Go dependency extraction."""
        with patch.object(Path, "exists", return_value=True):
>           result = self.scraper._extract_go_dependencies()
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E           AttributeError: 'DataScraper' object has no attribute '_extract_go_dependencies'

tests/test_data_scraper.py:463: AttributeError
__ TestDataScraperDependencyAnalysis.test_extract_java_dependencies_with_pom ___

self = <tests.test_data_scraper.TestDataScraperDependencyAnalysis testMethod=test_extract_java_dependencies_with_pom>

    def test_extract_java_dependencies_with_pom(self):
        """Test Java dependency extraction with pom.xml."""
        with patch.object(Path, "exists", return_value=True):
>           result = self.scraper._extract_java_dependencies()
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E           AttributeError: 'DataScraper' object has no attribute '_extract_java_dependencies'

tests/test_data_scraper.py:453: AttributeError
_ TestDataScraperDependencyAnalysis.test_extract_javascript_dependencies_invalid_json _

self = <tests.test_data_scraper.TestDataScraperDependencyAnalysis testMethod=test_extract_javascript_dependencies_invalid_json>

    def test_extract_javascript_dependencies_invalid_json(self):
        """Test JavaScript dependency extraction with invalid JSON."""
        mock_invalid_json = '{"dependencies": invalid json}'
    
        with patch("builtins.open", mock_open(read_data=mock_invalid_json)):
            with patch.object(Path, "exists", return_value=True):
>               result = self.scraper._extract_javascript_dependencies()
                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               AttributeError: 'DataScraper' object has no attribute '_extract_javascript_dependencies'

tests/test_data_scraper.py:432: AttributeError
_ TestDataScraperDependencyAnalysis.test_extract_javascript_dependencies_with_package_json _

self = <tests.test_data_scraper.TestDataScraperDependencyAnalysis testMethod=test_extract_javascript_dependencies_with_package_json>

    def test_extract_javascript_dependencies_with_package_json(self):
        """Test JavaScript dependency extraction with package.json."""
        mock_package_json = '{"dependencies": {"react": "^18.0.0"}, "devDependencies": {"jest": "^29.0.0"}}'
    
        with patch("builtins.open", mock_open(read_data=mock_package_json)):
            with patch.object(Path, "exists", return_value=True):
>               result = self.scraper._extract_javascript_dependencies()
                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               AttributeError: 'DataScraper' object has no attribute '_extract_javascript_dependencies'

tests/test_data_scraper.py:443: AttributeError
__ TestDataScraperDependencyAnalysis.test_extract_python_dependencies_no_file __

self = <tests.test_data_scraper.TestDataScraperDependencyAnalysis testMethod=test_extract_python_dependencies_no_file>

    def test_extract_python_dependencies_no_file(self):
        """Test Python dependency extraction when no requirements.txt exists."""
        with patch.object(Path, "exists", return_value=False):
>           result = self.scraper._extract_python_dependencies()
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E           AttributeError: 'DataScraper' object has no attribute '_extract_python_dependencies'

tests/test_data_scraper.py:423: AttributeError
_ TestDataScraperDependencyAnalysis.test_extract_python_dependencies_with_requirements _

self = <tests.test_data_scraper.TestDataScraperDependencyAnalysis testMethod=test_extract_python_dependencies_with_requirements>

    def test_extract_python_dependencies_with_requirements(self):
        """Test Python dependency extraction with requirements.txt."""
        mock_requirements = "requests>=2.31.0\npytest>=7.4.2\n"
    
        with patch("builtins.open", mock_open(read_data=mock_requirements)):
            with patch.object(Path, "exists", return_value=True):
>               result = self.scraper._extract_python_dependencies()
                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               AttributeError: 'DataScraper' object has no attribute '_extract_python_dependencies'

tests/test_data_scraper.py:413: AttributeError
_______ TestDataScraperDependencyAnalysis.test_extract_rust_dependencies _______

self = <tests.test_data_scraper.TestDataScraperDependencyAnalysis testMethod=test_extract_rust_dependencies>

    def test_extract_rust_dependencies(self):
        """Test Rust dependency extraction."""
        with patch.object(Path, "exists", return_value=True):
>           result = self.scraper._extract_rust_dependencies()
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E           AttributeError: 'DataScraper' object has no attribute '_extract_rust_dependencies'

tests/test_data_scraper.py:473: AttributeError
________________ TestDataScraperStringMethods.test_repr_method _________________

self = <tests.test_data_scraper.TestDataScraperStringMethods testMethod=test_repr_method>

    def test_repr_method(self):
        """Test __repr__ method."""
        repr_str = repr(self.scraper)
        self.assertIn("DataScraper", repr_str)
>       self.assertIn(str(self.repo_path), repr_str)
E       AssertionError: '/Users/dhodgson/Desktop/Ticket-Master' not found in '<src.ticket_master_consolidated.DataScraper object at 0x10ae33980>'

tests/test_data_scraper.py:498: AssertionError
_________________ TestDataScraperStringMethods.test_str_method _________________

self = <tests.test_data_scraper.TestDataScraperStringMethods testMethod=test_str_method>

    def test_str_method(self):
        """Test __str__ method."""
        str_repr = str(self.scraper)
        self.assertIn("DataScraper", str_repr)
>       self.assertIn(str(self.repo_path), str_repr)
E       AssertionError: '/Users/dhodgson/Desktop/Ticket-Master' not found in '<src.ticket_master_consolidated.DataScraper object at 0x10ae32ba0>'

tests/test_data_scraper.py:492: AssertionError
_________________ TestUserDatabase.test_cache_repository_data __________________

self = <tests.test_database.TestUserDatabase testMethod=test_cache_repository_data>

    def test_cache_repository_data(self):
        """Test repository data caching."""
>       with self.db:
             ^^^^^^^
E       TypeError: 'UserDatabase' object does not support the context manager protocol

tests/test_database.py:86: TypeError
___________________ TestUserDatabase.test_connect_disconnect ___________________

self = <tests.test_database.TestUserDatabase testMethod=test_connect_disconnect>

    def test_connect_disconnect(self):
        """Test database connection and disconnection."""
>       self.assertFalse(self.db.is_connected())
E       AssertionError: True is not false

tests/test_database.py:48: AssertionError
____________________ TestUserDatabase.test_context_manager _____________________

self = <tests.test_database.TestUserDatabase testMethod=test_context_manager>

    def test_context_manager(self):
        """Test database context manager."""
>       with self.db as db:
             ^^^^^^^
E       TypeError: 'UserDatabase' object does not support the context manager protocol

tests/test_database.py:58: TypeError
_____________________ TestUserDatabase.test_create_tables ______________________

self = <tests.test_database.TestUserDatabase testMethod=test_create_tables>

    def test_create_tables(self):
        """Test table creation."""
>       with self.db:
             ^^^^^^^
E       TypeError: 'UserDatabase' object does not support the context manager protocol

tests/test_database.py:64: TypeError
____________________ TestUserDatabase.test_user_preferences ____________________

self = <tests.test_database.TestUserDatabase testMethod=test_user_preferences>

    def test_user_preferences(self):
        """Test user preference storage and retrieval."""
>       with self.db:
             ^^^^^^^
E       TypeError: 'UserDatabase' object does not support the context manager protocol

tests/test_database.py:70: TypeError
___________________ TestEdgeCases.test_empty_string_handling ___________________

self = <tests.test_edge_cases.TestEdgeCases object at 0x10a9cd310>

    def test_empty_string_handling(self):
        """Test that modules handle empty strings gracefully."""
>       from colors import colorize, error, success
E       ModuleNotFoundError: No module named 'colors'

tests/test_edge_cases.py:24: ModuleNotFoundError
____________________ TestEdgeCases.test_none_value_handling ____________________

self = <tests.test_edge_cases.TestEdgeCases object at 0x10a9cd490>

    def test_none_value_handling(self):
        """Test that modules handle None values gracefully."""
>       from colors import colorize
E       ModuleNotFoundError: No module named 'colors'

tests/test_edge_cases.py:37: ModuleNotFoundError
_____________________ TestEdgeCases.test_unicode_handling ______________________

self = <tests.test_edge_cases.TestEdgeCases object at 0x10a9cd610>

    def test_unicode_handling(self):
        """Test Unicode string handling across modules."""
>       from colors import colorize, error, success
E       ModuleNotFoundError: No module named 'colors'

tests/test_edge_cases.py:50: ModuleNotFoundError
_____________________ TestEdgeCases.test_very_long_strings _____________________

self = <tests.test_edge_cases.TestEdgeCases object at 0x10a9cd790>

    def test_very_long_strings(self):
        """Test handling of very long strings."""
>       from colors import colorize, success
E       ModuleNotFoundError: No module named 'colors'

tests/test_edge_cases.py:65: ModuleNotFoundError
_____________________ TestEdgeCases.test_multiline_strings _____________________

self = <tests.test_edge_cases.TestEdgeCases object at 0x10a9cd910>

    def test_multiline_strings(self):
        """Test handling of multiline strings."""
>       from colors import info, warning
E       ModuleNotFoundError: No module named 'colors'

tests/test_edge_cases.py:76: ModuleNotFoundError
____________________ TestEdgeCases.test_special_characters _____________________

self = <tests.test_edge_cases.TestEdgeCases object at 0x10a9cda90>

    def test_special_characters(self):
        """Test handling of special characters."""
>       from colors import dim, highlight
E       ModuleNotFoundError: No module named 'colors'

tests/test_edge_cases.py:90: ModuleNotFoundError
________________ TestErrorConditions.test_stdout_without_isatty ________________

self = <tests.test_edge_cases.TestErrorConditions object at 0x10a9cdc40>
mock_stdout = <MagicMock name='stdout' id='4477623696'>

    @patch("sys.stdout")
    def test_stdout_without_isatty(self, mock_stdout):
        """Test color support detection when stdout lacks isatty."""
        # Remove isatty method
        if hasattr(mock_stdout, "isatty"):
            delattr(mock_stdout, "isatty")
    
>       from colors import supports_color
E       ModuleNotFoundError: No module named 'colors'

tests/test_edge_cases.py:111: ModuleNotFoundError
_______________ TestErrorConditions.test_empty_term_environment ________________

self = <tests.test_edge_cases.TestErrorConditions object at 0x10a9cddf0>

    @patch.dict(os.environ, {"TERM": ""})
    def test_empty_term_environment(self):
        """Test color support with empty TERM environment variable."""
>       from colors import supports_color
E       ModuleNotFoundError: No module named 'colors'

tests/test_edge_cases.py:120: ModuleNotFoundError
______________ TestErrorConditions.test_progress_bar_edge_values _______________

self = <tests.test_edge_cases.TestErrorConditions object at 0x10a9cdf70>

    def test_progress_bar_edge_values(self):
        """Test progress bar with edge case values."""
>       from colors import progress_bar
E       ModuleNotFoundError: No module named 'colors'

tests/test_edge_cases.py:131: ModuleNotFoundError
____________ TestErrorConditions.test_color_constants_immutability _____________

self = <tests.test_edge_cases.TestErrorConditions object at 0x10a9ce0f0>

    def test_color_constants_immutability(self):
        """Test that color constants exist and are strings."""
>       from colors import Colors
E       ModuleNotFoundError: No module named 'colors'

tests/test_edge_cases.py:152: ModuleNotFoundError
_______________ TestErrorConditions.test_global_color_variables ________________

self = <tests.test_edge_cases.TestErrorConditions object at 0x10a9ce270>

    def test_global_color_variables(self):
        """Test global color variables are properly defined."""
>       from colors import BLUE, BOLD, GREEN, RED, RESET
E       ModuleNotFoundError: No module named 'colors'

tests/test_edge_cases.py:167: ModuleNotFoundError
_________ TestModuleStructure.test_colors_module_has_required_exports __________

self = <tests.test_edge_cases.TestModuleStructure object at 0x10a9ce4b0>

    def test_colors_module_has_required_exports(self):
        """Test that colors module exports all required functions."""
>       import colors as colors
E       ModuleNotFoundError: No module named 'colors'

tests/test_edge_cases.py:191: ModuleNotFoundError
________ TestModuleStructure.test_colors_module_has_required_constants _________

self = <tests.test_edge_cases.TestModuleStructure object at 0x10a9ce630>

    def test_colors_module_has_required_constants(self):
        """Test that colors module exports all required constants."""
>       import colors as colors
E       ModuleNotFoundError: No module named 'colors'

tests/test_edge_cases.py:217: ModuleNotFoundError
_________________ TestFunctionDefaults.test_colorize_defaults __________________

self = <tests.test_edge_cases.TestFunctionDefaults object at 0x10a9ce7b0>

    def test_colorize_defaults(self):
        """Test colorize function with default parameters."""
>       from colors import colorize, enable_colors
E       ModuleNotFoundError: No module named 'colors'

tests/test_edge_cases.py:254: ModuleNotFoundError
____________ TestFunctionDefaults.test_formatting_function_defaults ____________

self = <tests.test_edge_cases.TestFunctionDefaults object at 0x10a9ce930>

    def test_formatting_function_defaults(self):
        """Test formatting functions with default parameters."""
>       from colors import error, header, highlight, info, success, warning
E       ModuleNotFoundError: No module named 'colors'

tests/test_edge_cases.py:273: ModuleNotFoundError
_______________ TestFunctionDefaults.test_progress_bar_defaults ________________

self = <tests.test_edge_cases.TestFunctionDefaults object at 0x10a9ceab0>

    def test_progress_bar_defaults(self):
        """Test progress_bar function with default parameters."""
>       from colors import progress_bar
E       ModuleNotFoundError: No module named 'colors'

tests/test_edge_cases.py:287: ModuleNotFoundError
________________ TestFunctionDefaults.test_header_color_default ________________

self = <tests.test_edge_cases.TestFunctionDefaults object at 0x10a9cec30>

    def test_header_color_default(self):
        """Test header function color default."""
>       from colors import Colors, enable_colors, header
E       ModuleNotFoundError: No module named 'colors'

tests/test_edge_cases.py:299: ModuleNotFoundError
______________ TestFunctionDefaults.test_highlight_color_default _______________

self = <tests.test_edge_cases.TestFunctionDefaults object at 0x10a9cedb0>

    def test_highlight_color_default(self):
        """Test highlight function color default."""
>       from colors import Colors, enable_colors, highlight
E       ModuleNotFoundError: No module named 'colors'

tests/test_edge_cases.py:310: ModuleNotFoundError
_____________________ TestCommit.test_init_invalid_commit ______________________

self = <tests.test_git_objects.TestCommit object at 0x10a9f4380>

    def test_init_invalid_commit(self):
        """Test Commit initialization with invalid input."""
        with pytest.raises(CommitError):
>           Commit("not_a_commit")

tests/test_git_objects.py:71: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <[AttributeError("'Commit' object has no attribute 'date'") raised in repr()] Commit object at 0x10af7bda0>
commit_data = 'not_a_commit'

    def __init__(self, commit_data) -> None:
        """Initialize Commit from git commit object or commit data dictionary."""
        if hasattr(commit_data, "hexsha"):
            # Git commit object
            self.git_commit = commit_data
            self.hash = commit_data.hexsha
            self.short_hash = commit_data.hexsha[:8]
    
            # Author info
            self.author = {
                "name": getattr(commit_data.author, "name", "Unknown"),
                "email": getattr(
                    commit_data.author, "email", "unknown@example.com"
                ),
            }
    
            # Committer info
            self.committer = {
                "name": getattr(commit_data.committer, "name", "Unknown"),
                "email": getattr(
                    commit_data.committer, "email", "unknown@example.com"
                ),
            }
    
            self.message = getattr(commit_data, "message", "")
            self.summary = getattr(
                commit_data, "summary", self.message.split("\n")[0]
            )
    
            # Date handling
            if hasattr(commit_data, "committed_datetime"):
                self.date = commit_data.committed_datetime
            elif hasattr(commit_data, "committed_date"):
                from datetime import datetime
    
                self.date = datetime.fromtimestamp(commit_data.committed_date)
            else:
                self.date = datetime.now()
    
            # Stats
            try:
                if hasattr(commit_data, "stats"):
                    stats = commit_data.stats
                    if hasattr(stats, "total"):
                        self.insertions = stats.total.get("insertions", 0)
                        self.deletions = stats.total.get("deletions", 0)
                        self.files_changed = len(getattr(stats, "files", {}))
                    else:
                        self.insertions = 0
                        self.deletions = 0
                        self.files_changed = 0
                else:
                    self.insertions = 0
                    self.deletions = 0
                    self.files_changed = 0
            except:
                self.insertions = 0
                self.deletions = 0
                self.files_changed = 0
    
        else:
            # Dictionary data (legacy compatibility)
            self.git_commit = None
>           self.hash = commit_data.get("hash", "")
                        ^^^^^^^^^^^^^^^
E           AttributeError: 'str' object has no attribute 'get'

src/ticket_master_consolidated.py:493: AttributeError
_________________________ TestCommit.test_get_parents __________________________

self = <tests.test_git_objects.TestCommit object at 0x10a9f60f0>
mock_git_commit = <Mock id='4478975440'>

    def test_get_parents(self, mock_git_commit):
        """Test getting parent commits."""
        parent1 = Mock()
        parent1.hexsha = "parent1hash"
        parent1.author.name = "Parent Author"
        parent1.author.email = "parent@example.com"
        parent1.committer.name = "Parent Committer"
        parent1.committer.email = "parent@example.com"
        parent1.message = "Parent commit"
        parent1.summary = "Parent commit"
        parent1.committed_date = 1640908800
        parent1.parents = []
        parent1.stats.total = {"insertions": 0, "deletions": 0, "files": 0}
        parent1.stats.files = {}
    
        mock_git_commit.parents = [parent1]
        commit = Commit(mock_git_commit)
    
        parents = commit.get_parents()
        assert len(parents) == 1
>       assert isinstance(parents[0], Commit)
E       AssertionError: assert False
E        +  where False = isinstance('parent1hash', Commit)

tests/test_git_objects.py:105: AssertionError
______________________ TestBranch.test_init_local_branch _______________________

self = <tests.test_git_objects.TestBranch object at 0x10a9f6b10>
mock_git_branch = <Mock id='4478972080'>

    def test_init_local_branch(self, mock_git_branch):
        """Test Branch initialization with local branch."""
        branch = Branch(mock_git_branch, is_active=True)
    
        assert branch.name == "feature/test-branch"
        assert branch.is_active is True
>       assert branch.is_remote is False
E       AssertionError: assert True is False
E        +  where True = Branch(name='feature/test-branch', is_active=True, is_remote=True, remote_name='feature').is_remote

tests/test_git_objects.py:229: AssertionError
_____________________ TestBranch.test_init_invalid_branch ______________________

self = <tests.test_git_objects.TestBranch object at 0x10a9f6ea0>

    def test_init_invalid_branch(self):
        """Test Branch initialization with invalid input."""
>       with pytest.raises(BranchError):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^
E       Failed: DID NOT RAISE <class 'src.ticket_master_consolidated.BranchError'>

tests/test_git_objects.py:246: Failed
______________________ TestBranch.test_get_last_activity _______________________

self = <tests.test_git_objects.TestBranch object at 0x10a9f7050>
mock_git_branch = <Mock id='4478573392'>

    def test_get_last_activity(self, mock_git_branch):
        """Test getting last activity date."""
        branch = Branch(mock_git_branch, is_active=False)
>       last_activity = branch.get_last_activity()
                        ^^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: 'Branch' object has no attribute 'get_last_activity'

tests/test_git_objects.py:252: AttributeError
___________________________ TestBranch.test_to_dict ____________________________

self = <tests.test_git_objects.TestBranch object at 0x10a9f7230>
mock_git_branch = <Mock id='4478574352'>

    def test_to_dict(self, mock_git_branch):
        """Test converting branch to dictionary."""
        branch = Branch(mock_git_branch, is_active=True)
        branch_dict = branch.to_dict()
    
        assert branch_dict["name"] == "feature/test-branch"
        assert branch_dict["is_active"] is True
>       assert branch_dict["is_remote"] is False
E       assert True is False

tests/test_git_objects.py:264: AssertionError
______________________ TestPullRequest.test_init_valid_pr ______________________

self = <tests.test_git_objects.TestPullRequest object at 0x10a9f7a40>
mock_github_pr = <Mock id='4478577280'>

    def test_init_valid_pr(self, mock_github_pr):
        """Test PullRequest initialization with valid PyGithub PR."""
        pr = PullRequest(mock_github_pr)
    
        assert pr.number == 42
        assert pr.title == "Test Pull Request"
        assert pr.description == "This is a test pull request description"
        assert pr.state == "open"
>       assert pr.is_draft is False
               ^^^^^^^^^^^
E       AttributeError: 'PullRequest' object has no attribute 'is_draft'

tests/test_git_objects.py:367: AttributeError
_____________________ TestPullRequest.test_init_invalid_pr _____________________

self = <tests.test_git_objects.TestPullRequest object at 0x10a9f7980>

    def test_init_invalid_pr(self):
        """Test PullRequest initialization with invalid input."""
        with pytest.raises(PullRequestError):
>           PullRequest("not_a_pr")

tests/test_git_objects.py:380: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <[AttributeError("'PullRequest' object has no attribute 'number'") raised in repr()] PullRequest object at 0x10af1ae70>
pr_data = 'not_a_pr'

    def __init__(self, pr_data) -> None:
        """Initialize PullRequest from GitHub PR object or data dictionary."""
        if pr_data is None:
            raise PullRequestError("pr_data cannot be None")
    
        if hasattr(pr_data, "number"):
            # GitHub PR object
            self.pr_obj = pr_data
            self.number = pr_data.number
            self.title = getattr(pr_data, "title", "")
            self.body = getattr(pr_data, "body", "")
            self.description = self.body  # Alias for body
            self.state = getattr(pr_data, "state", "")
    
            # Author info
            if hasattr(pr_data, "user") and pr_data.user:
                self.author = {
                    "login": getattr(pr_data.user, "login", ""),
                    "name": getattr(pr_data.user, "name", ""),
                    "email": getattr(pr_data.user, "email", None),
                }
                self.author_name = getattr(pr_data.user, "name", "")
                self.author_email = getattr(pr_data.user, "email", None)
            else:
                self.author = {"login": "", "name": "", "email": None}
                self.author_name = ""
                self.author_email = None
    
            # Additional properties
            self.draft = getattr(pr_data, "draft", False)
            self.commits = getattr(pr_data, "commits", 0)
            self.changed_files = getattr(pr_data, "changed_files", 0)
            self.additions = getattr(pr_data, "additions", 0)
            self.deletions = getattr(pr_data, "deletions", 0)
            self.created_at = getattr(pr_data, "created_at", datetime.now())
            self.updated_at = getattr(pr_data, "updated_at", datetime.now())
            self.merged_at = getattr(pr_data, "merged_at", None)
            self.merged = getattr(pr_data, "merged", False)
            self.mergeable = getattr(pr_data, "mergeable", None)
    
            # Branch info
            if hasattr(pr_data, "head") and pr_data.head:
                self.head_ref = getattr(pr_data.head, "ref", "")
            else:
                self.head_ref = ""
    
            if hasattr(pr_data, "base") and pr_data.base:
                self.base_ref = getattr(pr_data.base, "ref", "")
            else:
                self.base_ref = ""
    
        else:
            # Dictionary data (legacy compatibility)
            self.pr_obj = None
>           self.number = pr_data.get("number", 0)
                          ^^^^^^^^^^^
E           AttributeError: 'str' object has no attribute 'get'

src/ticket_master_consolidated.py:709: AttributeError
______________________ TestPullRequest.test_is_mergeable _______________________

self = <tests.test_git_objects.TestPullRequest object at 0x10a9f7590>
mock_github_pr = <Mock id='4478581408'>

    def test_is_mergeable(self, mock_github_pr):
        """Test mergeable status check."""
        pr = PullRequest(mock_github_pr)
        assert pr.is_mergeable() is True
    
        # Test closed PR
        mock_github_pr.state = "closed"
        pr = PullRequest(mock_github_pr)
>       assert pr.is_mergeable() is False
E       AssertionError: assert True is False
E        +  where True = is_mergeable()
E        +    where is_mergeable = PullRequest(number=42, title='Test Pull Request', state='closed', author='{'login': 'testuser', 'name': 'Test User', 'email': 'test@example.com'}').is_mergeable

tests/test_git_objects.py:390: AssertionError
_________________________ TestPullRequest.test_to_dict _________________________

self = <tests.test_git_objects.TestPullRequest object at 0x10a9f6f90>
mock_github_pr = <Mock id='4478966176'>

    def test_to_dict(self, mock_github_pr):
        """Test converting pull request to dictionary."""
        pr = PullRequest(mock_github_pr)
        pr_dict = pr.to_dict()
    
        assert pr_dict["number"] == 42
        assert pr_dict["title"] == "Test Pull Request"
        assert pr_dict["state"] == "open"
        assert pr_dict["source_branch"] == "feature/test-branch"
        assert pr_dict["target_branch"] == "main"
>       assert pr_dict["commits_count"] == 3
               ^^^^^^^^^^^^^^^^^^^^^^^^
E       KeyError: 'commits_count'

tests/test_git_objects.py:408: KeyError
___________________ TestPullRequest.test_str_representation ____________________

self = <tests.test_git_objects.TestPullRequest object at 0x10a9f66c0>
mock_github_pr = <Mock id='4466806608'>

    def test_str_representation(self, mock_github_pr):
        """Test string representation of pull request."""
        pr = PullRequest(mock_github_pr)
>       assert str(pr) == "PR #42 (OPEN): Test Pull Request"
E       AssertionError: assert '#42: Test Pull Request' == 'PR #42 (OPEN... Pull Request'
E         
E         - PR #42 (OPEN): Test Pull Request
E         ? ---   -------
E         + #42: Test Pull Request

tests/test_git_objects.py:418: AssertionError
____________ TestRepositoryIntegration.test_repository_get_commits _____________

self = <tests.test_git_objects.TestRepositoryIntegration object at 0x10a9f7e00>
temp_git_repo = '/var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmpb1oafp0u/test_repo'

    def test_repository_get_commits(self, temp_git_repo):
        """Test Repository.get_commits() returns Commit objects."""
        repo = Repository(temp_git_repo)
>       commits = repo.get_commits(max_count=10)
                  ^^^^^^^^^^^^^^^^
E       AttributeError: 'Repository' object has no attribute 'get_commits'

tests/test_git_objects.py:506: AttributeError
---------------------------- Captured stdout setup -----------------------------
Initialized empty Git repository in /private/var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmpb1oafp0u/test_repo/.git/
[master (root-commit) 74045bd] Initial commit
 1 file changed, 1 insertion(+)
 create mode 100644 README.md
[feature/test 9c16ef0] Add test file
 1 file changed, 1 insertion(+)
 create mode 100644 test.txt
---------------------------- Captured stderr setup -----------------------------
Switched to a new branch 'feature/test'
Switched to branch 'master'
____________ TestRepositoryIntegration.test_repository_get_branches ____________

self = <tests.test_git_objects.TestRepositoryIntegration object at 0x10aa14050>
temp_git_repo = '/var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmp8i8xaj5j/test_repo'

    def test_repository_get_branches(self, temp_git_repo):
        """Test Repository.get_branches() returns Branch objects."""
        repo = Repository(temp_git_repo)
>       branches = repo.get_branches()
                   ^^^^^^^^^^^^^^^^^
E       AttributeError: 'Repository' object has no attribute 'get_branches'

tests/test_git_objects.py:521: AttributeError
---------------------------- Captured stdout setup -----------------------------
Initialized empty Git repository in /private/var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmp8i8xaj5j/test_repo/.git/
[master (root-commit) 74045bd] Initial commit
 1 file changed, 1 insertion(+)
 create mode 100644 README.md
[feature/test 9c16ef0] Add test file
 1 file changed, 1 insertion(+)
 create mode 100644 test.txt
---------------------------- Captured stderr setup -----------------------------
Switched to a new branch 'feature/test'
Switched to branch 'master'
_____________ TestRepositoryIntegration.test_repository_get_commit _____________

self = <tests.test_git_objects.TestRepositoryIntegration object at 0x10aa14200>
temp_git_repo = '/var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmplfq_iopr/test_repo'

    def test_repository_get_commit(self, temp_git_repo):
        """Test Repository.get_commit() returns specific Commit object."""
        repo = Repository(temp_git_repo)
>       commits = repo.get_commits(max_count=1)
                  ^^^^^^^^^^^^^^^^
E       AttributeError: 'Repository' object has no attribute 'get_commits'

tests/test_git_objects.py:539: AttributeError
---------------------------- Captured stdout setup -----------------------------
Initialized empty Git repository in /private/var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmplfq_iopr/test_repo/.git/
[master (root-commit) 0429156] Initial commit
 1 file changed, 1 insertion(+)
 create mode 100644 README.md
[feature/test aa4d498] Add test file
 1 file changed, 1 insertion(+)
 create mode 100644 test.txt
---------------------------- Captured stderr setup -----------------------------
Switched to a new branch 'feature/test'
Switched to branch 'master'
_____________ TestRepositoryIntegration.test_repository_get_branch _____________

self = <tests.test_git_objects.TestRepositoryIntegration object at 0x10aa143e0>
temp_git_repo = '/var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmplix_hmtv/test_repo'

    def test_repository_get_branch(self, temp_git_repo):
        """Test Repository.get_branch() returns specific Branch object."""
        repo = Repository(temp_git_repo)
    
        # Get master branch (default in older Git versions)
>       master_branch = repo.get_branch("master")
                        ^^^^^^^^^^^^^^^
E       AttributeError: 'Repository' object has no attribute 'get_branch'

tests/test_git_objects.py:552: AttributeError
---------------------------- Captured stdout setup -----------------------------
Initialized empty Git repository in /private/var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmplix_hmtv/test_repo/.git/
[master (root-commit) 0429156] Initial commit
 1 file changed, 1 insertion(+)
 create mode 100644 README.md
[feature/test aa4d498] Add test file
 1 file changed, 1 insertion(+)
 create mode 100644 test.txt
---------------------------- Captured stderr setup -----------------------------
Switched to a new branch 'feature/test'
Switched to branch 'master'
________ TestRepositoryIntegration.test_repository_get_branch_not_found ________

self = <tests.test_git_objects.TestRepositoryIntegration object at 0x10aa145c0>
temp_git_repo = '/var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmpy82qukc3/test_repo'

    def test_repository_get_branch_not_found(self, temp_git_repo):
        """Test Repository.get_branch() raises error for non-existent branch."""
        repo = Repository(temp_git_repo)
    
        with pytest.raises(RepositoryError):
>           repo.get_branch("non-existent-branch")
            ^^^^^^^^^^^^^^^
E           AttributeError: 'Repository' object has no attribute 'get_branch'

tests/test_git_objects.py:566: AttributeError
---------------------------- Captured stdout setup -----------------------------
Initialized empty Git repository in /private/var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmpy82qukc3/test_repo/.git/
[master (root-commit) 0429156] Initial commit
 1 file changed, 1 insertion(+)
 create mode 100644 README.md
[feature/test aa4d498] Add test file
 1 file changed, 1 insertion(+)
 create mode 100644 test.txt
---------------------------- Captured stderr setup -----------------------------
Switched to a new branch 'feature/test'
Switched to branch 'master'
____________ TestGitHubUtils.test_parse_github_url_https_with_path _____________

self = <tests.test_github_utils.TestGitHubUtils object at 0x10aa17110>

    def test_parse_github_url_https_with_path(self):
        """Test parsing GitHub URL with additional path components."""
>       result = self.github_utils.parse_github_url(
            "https://github.com/owner/repo/issues"
        )

tests/test_github_utils.py:42: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <src.ticket_master_consolidated.GitHubUtils object at 0x10ace8200>
url_or_repo = 'https://github.com/owner/repo/issues'

    def parse_github_url(self, url_or_repo: str) -> str:
        """Parse GitHub URL or repository string to extract owner/repo format."""
        # Remove common prefixes and suffixes
        cleaned = url_or_repo.strip()
    
        if cleaned.startswith("https://github.com/"):
            cleaned = cleaned[19:]  # Remove "https://github.com/"
        elif cleaned.startswith("http://github.com/"):
            cleaned = cleaned[18:]  # Remove "http://github.com/"
        elif cleaned.startswith("git@github.com:"):
            cleaned = cleaned[15:]  # Remove "git@github.com:"
    
        if cleaned.endswith(".git"):
            cleaned = cleaned[:-4]  # Remove ".git"
    
        # Validate format
        parts = cleaned.split("/")
        if len(parts) != 2:
>           raise ValueError(
                f"Invalid GitHub repository format: {url_or_repo}. Expected format: 'owner/repo'"
            )
E           ValueError: Invalid GitHub repository format: https://github.com/owner/repo/issues. Expected format: 'owner/repo'

src/ticket_master_consolidated.py:2073: ValueError
___________ TestGitHubUtils.test_parse_github_url_non_github_domain ____________

self = <tests.test_github_utils.TestGitHubUtils object at 0x10aa17470>

    def test_parse_github_url_non_github_domain(self):
        """Test parsing URL from non-GitHub domain."""
        with pytest.raises(ValueError, match="URL must be from github.com"):
>           self.github_utils.parse_github_url("https://gitlab.com/owner/repo")

tests/test_github_utils.py:57: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <src.ticket_master_consolidated.GitHubUtils object at 0x10aca2b70>
url_or_repo = 'https://gitlab.com/owner/repo'

    def parse_github_url(self, url_or_repo: str) -> str:
        """Parse GitHub URL or repository string to extract owner/repo format."""
        # Remove common prefixes and suffixes
        cleaned = url_or_repo.strip()
    
        if cleaned.startswith("https://github.com/"):
            cleaned = cleaned[19:]  # Remove "https://github.com/"
        elif cleaned.startswith("http://github.com/"):
            cleaned = cleaned[18:]  # Remove "http://github.com/"
        elif cleaned.startswith("git@github.com:"):
            cleaned = cleaned[15:]  # Remove "git@github.com:"
    
        if cleaned.endswith(".git"):
            cleaned = cleaned[:-4]  # Remove ".git"
    
        # Validate format
        parts = cleaned.split("/")
        if len(parts) != 2:
>           raise ValueError(
                f"Invalid GitHub repository format: {url_or_repo}. Expected format: 'owner/repo'"
            )
E           ValueError: Invalid GitHub repository format: https://gitlab.com/owner/repo. Expected format: 'owner/repo'

src/ticket_master_consolidated.py:2073: ValueError

During handling of the above exception, another exception occurred:

self = <tests.test_github_utils.TestGitHubUtils object at 0x10aa17470>

    def test_parse_github_url_non_github_domain(self):
        """Test parsing URL from non-GitHub domain."""
>       with pytest.raises(ValueError, match="URL must be from github.com"):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AssertionError: Regex pattern did not match.
E        Regex: 'URL must be from github.com'
E        Input: "Invalid GitHub repository format: https://gitlab.com/owner/repo. Expected format: 'owner/repo'"

tests/test_github_utils.py:56: AssertionError
____ TestGitHubUtils.test_is_public_repository_rate_limited_fallback_public ____

self = <tests.test_github_utils.TestGitHubUtils object at 0x10aa17b30>
mock_get = <MagicMock name='get' id='4475124048'>
mock_subprocess = <MagicMock name='run' id='4478970208'>

    @patch("subprocess.run")
    @patch("ticket_master_consolidated.requests.get")
    def test_is_public_repository_rate_limited_fallback_public(
        self, mock_get, mock_subprocess
    ):
        """Test fallback to git ls-remote when rate limited for public repo."""
        # Mock 403 response (rate limited)
        mock_response = Mock()
        mock_response.status_code = 403
        mock_get.return_value = mock_response
    
        # Mock successful git ls-remote
        mock_subprocess.return_value = Mock(returncode=0)
    
        result = self.github_utils.is_public_repository("owner/repo")
>       assert result is True
E       assert False is True

tests/test_github_utils.py:109: AssertionError
------------------------------ Captured log call -------------------------------
WARNING  GitHubUtils:ticket_master_consolidated.py:2097 Unexpected response checking repository visibility: 403
_______________ TestGitHubUtils.test_get_repository_info_success _______________

self = <tests.test_github_utils.TestGitHubUtils object at 0x10aa17e90>
mock_get = <MagicMock name='get' id='4476279584'>

    @patch("ticket_master_consolidated.requests.get")
    def test_get_repository_info_success(self, mock_get):
        """Test getting repository info successfully."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": "repo",
            "full_name": "owner/repo",
            "description": "Test repository",
            "private": False,
            "clone_url": "https://github.com/owner/repo.git",
            "ssh_url": "git@github.com:owner/repo.git",
            "default_branch": "main",
            "language": "Python",
            "size": 1000,
        }
        mock_get.return_value = mock_response
    
>       result = self.github_utils.get_repository_info("owner/repo")
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: 'GitHubUtils' object has no attribute 'get_repository_info'

tests/test_github_utils.py:147: AttributeError
____________ TestGitHubUtils.test_get_repository_info_rate_limited _____________

self = <tests.test_github_utils.TestGitHubUtils object at 0x10aa44080>
mock_get = <MagicMock name='get' id='4476276032'>

    @patch("ticket_master_consolidated.requests.get")
    def test_get_repository_info_rate_limited(self, mock_get):
        """Test getting repository info when rate limited."""
        # Mock 403 response (rate limited)
        mock_response = Mock()
        mock_response.status_code = 403
        mock_get.return_value = mock_response
    
>       result = self.github_utils.get_repository_info("owner/repo")
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: 'GitHubUtils' object has no attribute 'get_repository_info'

tests/test_github_utils.py:162: AttributeError
_____________ TestGitHubUtils.test_clone_repository_public_success _____________

args = (<tests.test_github_utils.TestGitHubUtils object at 0x10aa44230>,)
keywargs = {}

    @wraps(func)
    def patched(*args, **keywargs):
>       with self.decoration_helper(patched,
                                    args,
                                    keywargs) as (newargs, newkeywargs):

/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1393: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/contextlib.py:137: in __enter__
    return next(self.gen)
           ^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1375: in decoration_helper
    arg = exit_stack.enter_context(patching)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/contextlib.py:526: in enter_context
    result = _enter(cm)
             ^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1467: in __enter__
    original, local = self.get_original()
                      ^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <unittest.mock._patch object at 0x10aa16090>

    def get_original(self):
        target = self.getter()
        name = self.attribute
    
        original = DEFAULT
        local = False
    
        try:
            original = target.__dict__[name]
        except (AttributeError, KeyError):
            original = getattr(target, name, DEFAULT)
        else:
            local = True
    
        if name in _builtins and isinstance(target, ModuleType):
            self.create = True
    
        if not self.create and original is DEFAULT:
>           raise AttributeError(
                "%s does not have the attribute %r" % (target, name)
            )
E           AttributeError: <class 'ticket_master_consolidated.GitHubUtils'> does not have the attribute 'get_repository_info'

/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1437: AttributeError
___________ TestGitHubUtils.test_clone_repository_private_with_token ___________

args = (<tests.test_github_utils.TestGitHubUtils object at 0x10aa443e0>,)
keywargs = {}

    @wraps(func)
    def patched(*args, **keywargs):
>       with self.decoration_helper(patched,
                                    args,
                                    keywargs) as (newargs, newkeywargs):

/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1393: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/contextlib.py:137: in __enter__
    return next(self.gen)
           ^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1375: in decoration_helper
    arg = exit_stack.enter_context(patching)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/contextlib.py:526: in enter_context
    result = _enter(cm)
             ^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1467: in __enter__
    original, local = self.get_original()
                      ^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <unittest.mock._patch object at 0x10aa161e0>

    def get_original(self):
        target = self.getter()
        name = self.attribute
    
        original = DEFAULT
        local = False
    
        try:
            original = target.__dict__[name]
        except (AttributeError, KeyError):
            original = getattr(target, name, DEFAULT)
        else:
            local = True
    
        if name in _builtins and isinstance(target, ModuleType):
            self.create = True
    
        if not self.create and original is DEFAULT:
>           raise AttributeError(
                "%s does not have the attribute %r" % (target, name)
            )
E           AttributeError: <class 'ticket_master_consolidated.GitHubUtils'> does not have the attribute 'get_repository_info'

/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1437: AttributeError
_______________ TestGitHubUtils.test_clone_repository_not_found ________________

args = (<tests.test_github_utils.TestGitHubUtils object at 0x10aa44590>,)
keywargs = {}

    @wraps(func)
    def patched(*args, **keywargs):
>       with self.decoration_helper(patched,
                                    args,
                                    keywargs) as (newargs, newkeywargs):

/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1393: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/contextlib.py:137: in __enter__
    return next(self.gen)
           ^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1375: in decoration_helper
    arg = exit_stack.enter_context(patching)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/contextlib.py:526: in enter_context
    result = _enter(cm)
             ^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1467: in __enter__
    original, local = self.get_original()
                      ^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <unittest.mock._patch object at 0x10aa16390>

    def get_original(self):
        target = self.getter()
        name = self.attribute
    
        original = DEFAULT
        local = False
    
        try:
            original = target.__dict__[name]
        except (AttributeError, KeyError):
            original = getattr(target, name, DEFAULT)
        else:
            local = True
    
        if name in _builtins and isinstance(target, ModuleType):
            self.create = True
    
        if not self.create and original is DEFAULT:
>           raise AttributeError(
                "%s does not have the attribute %r" % (target, name)
            )
E           AttributeError: <class 'ticket_master_consolidated.GitHubUtils'> does not have the attribute 'get_repository_info'

/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1437: AttributeError
_____________ TestGitHubUtils.test_clone_repository_to_local_path ______________

args = (<tests.test_github_utils.TestGitHubUtils object at 0x10aa44740>,)
keywargs = {}

    @wraps(func)
    def patched(*args, **keywargs):
>       with self.decoration_helper(patched,
                                    args,
                                    keywargs) as (newargs, newkeywargs):

/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1393: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/contextlib.py:137: in __enter__
    return next(self.gen)
           ^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1375: in decoration_helper
    arg = exit_stack.enter_context(patching)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/contextlib.py:526: in enter_context
    result = _enter(cm)
             ^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1467: in __enter__
    original, local = self.get_original()
                      ^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <unittest.mock._patch object at 0x10aa16420>

    def get_original(self):
        target = self.getter()
        name = self.attribute
    
        original = DEFAULT
        local = False
    
        try:
            original = target.__dict__[name]
        except (AttributeError, KeyError):
            original = getattr(target, name, DEFAULT)
        else:
            local = True
    
        if name in _builtins and isinstance(target, ModuleType):
            self.create = True
    
        if not self.create and original is DEFAULT:
>           raise AttributeError(
                "%s does not have the attribute %r" % (target, name)
            )
E           AttributeError: <class 'ticket_master_consolidated.GitHubUtils'> does not have the attribute 'get_repository_info'

/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1437: AttributeError
________________ TestGitHubUtils.test_cleanup_temp_directories _________________

self = <tests.test_github_utils.TestGitHubUtils object at 0x10aa44920>

    def test_cleanup_temp_directories(self):
        """Test cleanup of temporary directories."""
        # Create a mock temporary directory
        temp_dir = tempfile.mkdtemp()
>       self.github_utils._temp_dirs.append(temp_dir)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: 'GitHubUtils' object has no attribute '_temp_dirs'

tests/test_github_utils.py:255: AttributeError
___________________ TestGitHubUtils.test_destructor_cleanup ____________________

self = <tests.test_github_utils.TestGitHubUtils object at 0x10aa44ad0>

    def test_destructor_cleanup(self):
        """Test that cleanup happens in destructor."""
        # Create a new instance
        utils = GitHubUtils()
    
        # Create a mock temporary directory
        temp_dir = tempfile.mkdtemp()
>       utils._temp_dirs.append(temp_dir)
        ^^^^^^^^^^^^^^^^
E       AttributeError: 'GitHubUtils' object has no attribute '_temp_dirs'

tests/test_github_utils.py:274: AttributeError
____________ TestGitHubUtilsAdvanced.test_empty_repository_handling ____________

self = <tests.test_github_utils.TestGitHubUtilsAdvanced object at 0x10aa452b0>

    def test_empty_repository_handling(self):
        """Test handling of empty repositories."""
        # Create an empty temporary directory to simulate empty repo
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize as git repo but keep it empty
            import git
    
            repo = git.Repo.init(temp_dir)
    
            # Add a commit to avoid "reference does not exist" error
            # Create an empty commit
>           repo.index.commit("Initial empty commit", allow_empty=True)
E           TypeError: IndexFile.commit() got an unexpected keyword argument 'allow_empty'

tests/test_github_utils.py:502: TypeError
__________ TestEndToEndIntegration.test_llm_issue_generation_pipeline __________

self = <tests.test_integration.TestEndToEndIntegration testMethod=test_llm_issue_generation_pipeline>

    def test_llm_issue_generation_pipeline(self):
        """Test complete pipeline using LLM issue generation."""
        # Create minimal analysis data
        analysis = {
            "repository_info": {"name": "test-repo", "active_branch": "main"},
            "commits": [
                {
                    "hash": "abc123",
                    "short_hash": "abc123",
                    "summary": "Add new feature",
                    "author": {
                        "name": "Test User",
                        "email": "test@example.com",
                    },
                    "committer": {
                        "name": "Test User",
                        "email": "test@example.com",
                    },
                    "message": "Add new feature implementation",
                    "date": "2023-01-01T00:00:00",
                    "files_changed": 3,
                    "insertions": 50,
                    "deletions": 10,
                }
            ],
            "file_changes": {
                "modified_files": {
                    "src/main.py": {
                        "changes": 2,
                        "insertions": 30,
                        "deletions": 5,
                        "commits": ["abc123"],
                    }
                },
                "new_files": ["src/feature.py"],
                "deleted_files": [],
                "renamed_files": [],
                "summary": {
                    "total_files": 2,
                    "total_insertions": 50,
                    "total_deletions": 10,
                },
            },
            "analysis_summary": {
                "commit_count": 1,
                "files_modified": 1,
                "files_added": 1,
                "total_insertions": 50,
                "total_deletions": 10,
            },
        }
    
        # Test LLM issue generation
        issues = generate_issues_with_llm(analysis, self.test_config)
    
        # Verify results
        self.assertIsInstance(issues, list)
        self.assertGreater(len(issues), 0)
        self.assertLessEqual(
            len(issues), self.test_config["issue_generation"]["max_issues"]
        )
    
        # Check issue structure
        for issue in issues:
            self.assertIsNotNone(issue.title)
            self.assertIsNotNone(issue.description)
>           self.assertTrue(
                len(issue.description)
                >= self.test_config["issue_generation"][
                    "min_description_length"
                ]
            )
E           AssertionError: False is not true

tests/test_integration.py:168: AssertionError
------------------------------ Captured log call -------------------------------
ERROR    main:main.py:490 LLM error: Unsupported LLM provider: mock
________ TestEndToEndIntegration.test_sample_issue_generation_pipeline _________

self = <tests.test_integration.TestEndToEndIntegration testMethod=test_sample_issue_generation_pipeline>

    def test_sample_issue_generation_pipeline(self):
        """Test complete pipeline using sample issue generation."""
        # Create minimal analysis data
        analysis = {
            "repository_info": {"name": "test-repo", "active_branch": "main"},
            "commits": [
                {
                    "hash": "abc123",
                    "short_hash": "abc123",
                    "summary": "Test commit",
                    "author": {
                        "name": "Test User",
                        "email": "test@example.com",
                    },
                    "committer": {
                        "name": "Test User",
                        "email": "test@example.com",
                    },
                    "message": "Test commit message",
                    "date": "2023-01-01T00:00:00",
                    "files_changed": 1,
                    "insertions": 10,
                    "deletions": 5,
                }
            ],
            "file_changes": {
                "modified_files": {},
                "new_files": [],
                "deleted_files": [],
                "renamed_files": [],
                "summary": {
                    "total_files": 1,
                    "total_insertions": 10,
                    "total_deletions": 5,
                },
            },
            "analysis_summary": {
                "commit_count": 1,
                "files_modified": 1,
                "files_added": 0,
                "total_insertions": 10,
                "total_deletions": 5,
            },
        }
    
        # Test sample issue generation
        issues = generate_sample_issues(analysis, self.test_config)
    
        # Verify results
        self.assertIsInstance(issues, list)
        self.assertGreater(len(issues), 0)
    
        # Check first issue
        first_issue = issues[0]
        self.assertIsNotNone(first_issue.title)
        self.assertIsNotNone(first_issue.description)
>       self.assertIsInstance(first_issue.labels, list)
E       AssertionError: <MagicMock name='Issue().labels' id='4478398064'> is not an instance of <class 'list'>

tests/test_integration.py:99: AssertionError
________ TestTemplateCreation.test_create_issues_with_templates_success ________

self = <tests.test_issue.TestTemplateCreation object at 0x10aa988f0>
mock_bulk_create = <MagicMock name='create_bulk_issues' id='4475838800'>

    @patch("ticket_master_consolidated.Issue.create_bulk_issues")
    def test_create_issues_with_templates_success(self, mock_bulk_create):
        """Test successful template creation."""
        template_data = [
            {
                "title": "Template Issue 1",
                "description": "Template description 1",
                "labels": ["bug"],
            },
            {
                "title": "Template Issue 2",
                "description": "Template description 2",
                "labels": ["feature"],
                "assignees": ["user1"],
            },
        ]
    
        mock_bulk_create.return_value = {
            "success": True,
            "total_issues": 2,
            "created_count": 2,
            "failed_count": 0,
            "errors": [],
        }
    
>       result = Issue.create_issues_with_templates(
            "test/repo", template_data, default_labels=["automated"]
        )

tests/test_issue.py:883: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

cls = <class 'ticket_master_consolidated.Issue'>, repo_name = 'test/repo'
templates = [{'description': 'Template description 1', 'labels': ['bug', 'automated'], 'title': 'Template Issue 1'}, {'assignees': ['user1'], 'description': 'Template description 2', 'labels': ['feature', 'automated'], 'title': 'Template Issue 2'}]
token = None, default_labels = ['automated'], kwargs = {}
results = {'created_issues': [], 'success': True, 'template_errors': [], 'total_issues': 2}
issues = [Issue(title='Template Issue 1', description_length=22, labels=['bug', 'automated'], assignees=[], milestone='None'), ...tle='Template Issue 2', description_length=22, labels=['feature', 'automated'], assignees=['user1'], milestone='None')]
template = {'assignees': ['user1'], 'description': 'Template description 2', 'labels': ['feature', 'automated'], 'title': 'Template Issue 2'}
template_labels = ['feature']
issue = Issue(title='Template Issue 2', description_length=22, labels=['feature', 'automated'], assignees=['user1'], milestone='None')

    @classmethod
    def create_issues_with_templates(
        cls,
        repo_name: str,
        templates: List[Dict[str, Any]],
        token: Optional[str] = None,
        default_labels: Optional[List[str]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Create issues from template dictionaries.
    
        Args:
            repo_name: Repository name in 'owner/repo' format
            templates: List of dictionaries with issue templates
            token: GitHub API token, or None to use environment variable
            default_labels: Default labels to apply to all issues
            **kwargs: Additional arguments for create_bulk_issues
    
        Returns:
            Dictionary with results of bulk creation
        """
        results = {
            "success": True,
            "total_issues": len(templates),
            "created_issues": [],
            "template_errors": [],
        }
    
        if not templates:
            return results
    
        issues = []
    
        for template in templates:
            try:
                # Merge default labels with template labels
                if default_labels:
                    template_labels = template.get("labels", [])
                    if isinstance(template_labels, list):
                        template["labels"] = template_labels + [
                            label
                            for label in default_labels
                            if label not in template_labels
                        ]
                    else:
                        template["labels"] = default_labels
    
                # Create issue from template
                issue = cls.from_dict(template)
                issues.append(issue)
    
            except Exception as e:
                results["template_errors"].append(
                    {"template": template, "error": str(e)}
                )
                results["success"] = False
    
        if issues:
            bulk_results = cls.create_bulk_issues(
                issues, repo_name, token, **kwargs
            )
    
            # Merge results
            results.update(
                {
                    "success": bulk_results["success"],
>                   "created_issues": bulk_results["created_issues"],
                                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                    "failed_issues": bulk_results.get("failed_issues", []),
                    "errors": bulk_results.get("errors", []),
                    "created_count": bulk_results.get("created_count", 0),
                    "failed_count": bulk_results.get("failed_count", 0),
                }
            )
E           KeyError: 'created_issues'

src/ticket_master_consolidated.py:1545: KeyError
____ TestTemplateCreation.test_create_issues_with_templates_creation_errors ____

self = <tests.test_issue.TestTemplateCreation object at 0x10aa98a40>
mock_bulk_create = <MagicMock name='create_bulk_issues' id='4472822272'>

    @patch("ticket_master_consolidated.Issue.create_bulk_issues")
    def test_create_issues_with_templates_creation_errors(
        self, mock_bulk_create
    ):
        """Test template creation with invalid template data."""
        template_data = [
            {"title": "Valid Issue", "description": "Valid description"},
            {"title": ""},  # Invalid - empty title
            {"description": "Missing title"},  # Invalid - no title
        ]
    
        mock_bulk_create.return_value = {
            "success": True,
            "created_count": 1,
            "errors": [],
        }
    
>       result = Issue.create_issues_with_templates("test/repo", template_data)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_issue.py:915: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

cls = <class 'ticket_master_consolidated.Issue'>, repo_name = 'test/repo'
templates = [{'description': 'Valid description', 'title': 'Valid Issue'}, {'title': ''}, {'description': 'Missing title'}]
token = None, default_labels = None, kwargs = {}
results = {'created_issues': [], 'success': False, 'template_errors': [{'error': 'Missing required field: description', 'templat...e': ''}}, {'error': 'Missing required field: title', 'template': {'description': 'Missing title'}}], 'total_issues': 3}
issues = [Issue(title='Valid Issue', description_length=17, labels=[], assignees=[], milestone='None')]
template = {'description': 'Missing title'}
issue = Issue(title='Valid Issue', description_length=17, labels=[], assignees=[], milestone='None')

    @classmethod
    def create_issues_with_templates(
        cls,
        repo_name: str,
        templates: List[Dict[str, Any]],
        token: Optional[str] = None,
        default_labels: Optional[List[str]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Create issues from template dictionaries.
    
        Args:
            repo_name: Repository name in 'owner/repo' format
            templates: List of dictionaries with issue templates
            token: GitHub API token, or None to use environment variable
            default_labels: Default labels to apply to all issues
            **kwargs: Additional arguments for create_bulk_issues
    
        Returns:
            Dictionary with results of bulk creation
        """
        results = {
            "success": True,
            "total_issues": len(templates),
            "created_issues": [],
            "template_errors": [],
        }
    
        if not templates:
            return results
    
        issues = []
    
        for template in templates:
            try:
                # Merge default labels with template labels
                if default_labels:
                    template_labels = template.get("labels", [])
                    if isinstance(template_labels, list):
                        template["labels"] = template_labels + [
                            label
                            for label in default_labels
                            if label not in template_labels
                        ]
                    else:
                        template["labels"] = default_labels
    
                # Create issue from template
                issue = cls.from_dict(template)
                issues.append(issue)
    
            except Exception as e:
                results["template_errors"].append(
                    {"template": template, "error": str(e)}
                )
                results["success"] = False
    
        if issues:
            bulk_results = cls.create_bulk_issues(
                issues, repo_name, token, **kwargs
            )
    
            # Merge results
            results.update(
                {
                    "success": bulk_results["success"],
>                   "created_issues": bulk_results["created_issues"],
                                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                    "failed_issues": bulk_results.get("failed_issues", []),
                    "errors": bulk_results.get("errors", []),
                    "created_count": bulk_results.get("created_count", 0),
                    "failed_count": bulk_results.get("failed_count", 0),
                }
            )
E           KeyError: 'created_issues'

src/ticket_master_consolidated.py:1545: KeyError
_______________ TestLLMBackend.test_mock_backend_get_model_info ________________

self = <tests.test_llm.TestLLMBackend testMethod=test_mock_backend_get_model_info>

    def test_mock_backend_get_model_info(self):
        """Test MockBackend model info."""
        backend = MockBackend({"model": "test-mock"})
    
        info = backend.get_model_info()
    
        self.assertEqual(info["name"], "test-mock")
        self.assertEqual(info["provider"], "mock")
        self.assertEqual(info["status"], "available")
>       self.assertIn("description", info)
E       AssertionError: 'description' not found in {'name': 'test-mock', 'provider': 'mock', 'status': 'available'}

tests/test_llm.py:166: AssertionError
___________________ TestLLMBackend.test_openai_backend_init ____________________

self = <tests.test_llm.TestLLMBackend testMethod=test_openai_backend_init>

    def test_openai_backend_init(self):
        """Test OpenAIBackend initialization."""
        config = {"api_key": "test-api-key", "model": "gpt-4"}
    
        backend = OpenAIBackend(config)
    
        self.assertEqual(backend.api_key, "test-api-key")
        self.assertEqual(backend.model, "gpt-4")
>       self.assertEqual(backend.base_url, "https://api.openai.com/v1")
                         ^^^^^^^^^^^^^^^^
E       AttributeError: 'OpenAIBackend' object has no attribute 'base_url'

tests/test_llm.py:69: AttributeError
___________ TestLLMBackend.test_openai_backend_init_missing_api_key ____________

self = <tests.test_llm.TestLLMBackend testMethod=test_openai_backend_init_missing_api_key>

    def test_openai_backend_init_missing_api_key(self):
        """Test OpenAIBackend initialization without API key."""
        config = {"model": "gpt-4"}
    
>       with self.assertRaises(LLMProviderError) as context:
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AssertionError: LLMProviderError not raised

tests/test_llm.py:75: AssertionError
_____________________ TestLLMBackend.test_openai_generate ______________________

self = <tests.test_llm.TestLLMBackend testMethod=test_openai_generate>
mock_post = <MagicMock name='post' id='4478760480'>

    @patch("ticket_master_consolidated.requests.post")
    def test_openai_generate(self, mock_post):
        """Test OpenAI text generation."""
        backend = OpenAIBackend(
            {"api_key": "test-key", "model": "gpt-3.5-turbo"}
        )
    
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Generated text response"}}]
        }
        mock_post.return_value = mock_response
    
>       result = backend.generate("Test prompt")
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_llm.py:111: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <ticket_master_consolidated.OpenAIBackend object at 0x10af476e0>
prompt = 'Test prompt', kwargs = {}

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using OpenAI."""
>       raise LLMProviderError("OpenAI backend not fully implemented")
E       ticket_master_consolidated.LLMProviderError: OpenAI backend not fully implemented

src/ticket_master_consolidated.py:1753: LLMProviderError
__________________ TestLLMBackend.test_openai_generate_error ___________________

self = <tests.test_llm.TestLLMBackend testMethod=test_openai_generate_error>
mock_post = <MagicMock name='post' id='4478752272'>

    @patch("ticket_master_consolidated.requests.post")
    def test_openai_generate_error(self, mock_post):
        """Test OpenAI text generation with API error."""
        backend = OpenAIBackend({"api_key": "test-key"})
    
        # Mock error response
        mock_post.side_effect = Exception("API Error")
    
        with self.assertRaises(LLMProviderError) as context:
            backend.generate("Test prompt")
    
>       self.assertIn("API request failed", str(context.exception))
E       AssertionError: 'API request failed' not found in 'OpenAI backend not fully implemented'

tests/test_llm.py:135: AssertionError
___________________ TestLLMBackend.test_openai_is_available ____________________

self = <tests.test_llm.TestLLMBackend testMethod=test_openai_is_available>
mock_get = <MagicMock name='get' id='4476437952'>

    @patch("ticket_master_consolidated.requests.get")
    def test_openai_is_available(self, mock_get):
        """Test OpenAI availability check."""
        backend = OpenAIBackend({"api_key": "test-key"})
    
        # Test available
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
>       self.assertTrue(backend.is_available())
E       AssertionError: False is not true

tests/test_llm.py:89: AssertionError
_____________________ TestLLM.test_init_with_enum_provider _____________________

self = <tests.test_llm.TestLLM testMethod=test_init_with_enum_provider>

    def test_init_with_enum_provider(self):
        """Test LLM initialization with enum provider."""
        config = {"host": "localhost", "model": "test"}
>       llm = LLM(LLMProvider.OLLAMA, config)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_llm.py:206: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <ticket_master_consolidated.LLM object at 0x10ad12fc0>
provider = <LLMProvider.OLLAMA: 'ollama'>
config = {'host': 'localhost', 'model': 'test'}

    def __init__(self, provider: str, config: Dict[str, Any]) -> None:
        """Initialize LLM with specified provider and configuration."""
        self.provider = provider
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
        # Create appropriate backend
        if provider == "ollama":
            self.backend = OllamaBackend(config)
        else:
>           raise LLMError(f"Unsupported LLM provider: {provider}")
E           ticket_master_consolidated.LLMError: Unsupported LLM provider: LLMProvider.OLLAMA

src/ticket_master_consolidated.py:1781: LLMError
____________________ TestLLM.test_init_with_string_provider ____________________

self = <tests.test_llm.TestLLM testMethod=test_init_with_string_provider>

    def test_init_with_string_provider(self):
        """Test LLM initialization with string provider."""
        config = {"host": "localhost", "model": "test"}
        llm = LLM("ollama", config)
    
>       self.assertEqual(llm.provider, LLMProvider.OLLAMA)
E       AssertionError: 'ollama' != <LLMProvider.OLLAMA: 'ollama'>

tests/test_llm.py:200: AssertionError
_____________________ TestLLM.test_llm_generate_end_to_end _____________________

self = <tests.test_llm.TestLLM testMethod=test_llm_generate_end_to_end>

    def test_llm_generate_end_to_end(self):
        """Test end-to-end LLM generation workflow."""
        config = {"api_key": "test-key", "model": "gpt-3.5-turbo"}
>       llm = LLM(LLMProvider.OPENAI, config)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_llm.py:239: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <ticket_master_consolidated.LLM object at 0x10ad13530>
provider = <LLMProvider.OPENAI: 'openai'>
config = {'api_key': 'test-key', 'model': 'gpt-3.5-turbo'}

    def __init__(self, provider: str, config: Dict[str, Any]) -> None:
        """Initialize LLM with specified provider and configuration."""
        self.provider = provider
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
        # Create appropriate backend
        if provider == "ollama":
            self.backend = OllamaBackend(config)
        else:
>           raise LLMError(f"Unsupported LLM provider: {provider}")
E           ticket_master_consolidated.LLMError: Unsupported LLM provider: LLMProvider.OPENAI

src/ticket_master_consolidated.py:1781: LLMError
____________________________ TestLLM.test_metadata _____________________________

self = <tests.test_llm.TestLLM testMethod=test_metadata>

    def test_metadata(self):
        """Test LLM metadata."""
        config = {"model": "test_model"}
>       llm = LLM(LLMProvider.OLLAMA, config)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_llm.py:220: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <ticket_master_consolidated.LLM object at 0x10ad11220>
provider = <LLMProvider.OLLAMA: 'ollama'>, config = {'model': 'test_model'}

    def __init__(self, provider: str, config: Dict[str, Any]) -> None:
        """Initialize LLM with specified provider and configuration."""
        self.provider = provider
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
        # Create appropriate backend
        if provider == "ollama":
            self.backend = OllamaBackend(config)
        else:
>           raise LLMError(f"Unsupported LLM provider: {provider}")
E           ticket_master_consolidated.LLMError: Unsupported LLM provider: LLMProvider.OLLAMA

src/ticket_master_consolidated.py:1781: LLMError
______________________ TestLLM.test_mock_llm_integration _______________________

self = <tests.test_llm.TestLLM testMethod=test_mock_llm_integration>

    def test_mock_llm_integration(self):
        """Test complete Mock LLM integration."""
        config = {"model": "test-mock"}
>       llm = LLM("mock", config)
              ^^^^^^^^^^^^^^^^^^^

tests/test_llm.py:272: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <ticket_master_consolidated.LLM object at 0x10ad122d0>, provider = 'mock'
config = {'model': 'test-mock'}

    def __init__(self, provider: str, config: Dict[str, Any]) -> None:
        """Initialize LLM with specified provider and configuration."""
        self.provider = provider
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
        # Create appropriate backend
        if provider == "ollama":
            self.backend = OllamaBackend(config)
        else:
>           raise LLMError(f"Unsupported LLM provider: {provider}")
E           ticket_master_consolidated.LLMError: Unsupported LLM provider: mock

src/ticket_master_consolidated.py:1781: LLMError
______________________ TestLLM.test_openai_initialization ______________________

self = <tests.test_llm.TestLLM testMethod=test_openai_initialization>

    def test_openai_initialization(self):
        """Test LLM initialization with OpenAI provider."""
        config = {"api_key": "test-key", "model": "gpt-4"}
>       llm = LLM(LLMProvider.OPENAI, config)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_llm.py:230: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <ticket_master_consolidated.LLM object at 0x10af44410>
provider = <LLMProvider.OPENAI: 'openai'>
config = {'api_key': 'test-key', 'model': 'gpt-4'}

    def __init__(self, provider: str, config: Dict[str, Any]) -> None:
        """Initialize LLM with specified provider and configuration."""
        self.provider = provider
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
        # Create appropriate backend
        if provider == "ollama":
            self.backend = OllamaBackend(config)
        else:
>           raise LLMError(f"Unsupported LLM provider: {provider}")
E           ticket_master_consolidated.LLMError: Unsupported LLM provider: LLMProvider.OPENAI

src/ticket_master_consolidated.py:1781: LLMError
______ TestLLMModelInstallation.test_install_model_backend_not_supported _______

self = <tests.test_llm.TestLLMModelInstallation testMethod=test_install_model_backend_not_supported>

    def test_install_model_backend_not_supported(self):
        """Test model installation when backend doesn't support it."""
        config = {"host": "localhost", "port": 11434}
    
        # Create a mock backend without install_model method
        mock_backend = Mock(spec=[])  # No install_model method
>       with patch("llm.OllamaBackend", return_value=mock_backend):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_llm.py:338: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1451: in __enter__
    self.target = self.getter()
                  ^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pkgutil.py:513: in resolve_name
    mod = importlib.import_module(modname)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:1387: in _gcd_import
    ???
<frozen importlib._bootstrap>:1360: in _find_and_load
    ???
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

name = 'llm', import_ = <function _gcd_import at 0x1022ec0e0>

>   ???
E   ModuleNotFoundError: No module named 'llm'

<frozen importlib._bootstrap>:1324: ModuleNotFoundError
__________ TestLLMModelInstallation.test_install_model_ollama_success __________

self = <tests.test_llm.TestLLMModelInstallation testMethod=test_install_model_ollama_success>

    def test_install_model_ollama_success(self):
        """Test successful model installation with Ollama provider."""
        config = {"host": "localhost", "port": 11434, "model": "llama2"}
>       llm = LLM(LLMProvider.OLLAMA, config)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_llm.py:304: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <ticket_master_consolidated.LLM object at 0x10ad11010>
provider = <LLMProvider.OLLAMA: 'ollama'>
config = {'host': 'localhost', 'model': 'llama2', 'port': 11434}

    def __init__(self, provider: str, config: Dict[str, Any]) -> None:
        """Initialize LLM with specified provider and configuration."""
        self.provider = provider
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
        # Create appropriate backend
        if provider == "ollama":
            self.backend = OllamaBackend(config)
        else:
>           raise LLMError(f"Unsupported LLM provider: {provider}")
E           ticket_master_consolidated.LLMError: Unsupported LLM provider: LLMProvider.OLLAMA

src/ticket_master_consolidated.py:1781: LLMError
_______ TestLLMModelInstallation.test_install_model_unsupported_provider _______

self = <tests.test_llm.TestLLMModelInstallation testMethod=test_install_model_unsupported_provider>

    def test_install_model_unsupported_provider(self):
        """Test model installation with unsupported provider."""
        config = {"api_key": "test-key", "model": "gpt-4"}
>       llm = LLM(LLMProvider.OPENAI, config)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_llm.py:324: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <ticket_master_consolidated.LLM object at 0x10af47bc0>
provider = <LLMProvider.OPENAI: 'openai'>
config = {'api_key': 'test-key', 'model': 'gpt-4'}

    def __init__(self, provider: str, config: Dict[str, Any]) -> None:
        """Initialize LLM with specified provider and configuration."""
        self.provider = provider
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
        # Create appropriate backend
        if provider == "ollama":
            self.backend = OllamaBackend(config)
        else:
>           raise LLMError(f"Unsupported LLM provider: {provider}")
E           ticket_master_consolidated.LLMError: Unsupported LLM provider: LLMProvider.OPENAI

src/ticket_master_consolidated.py:1781: LLMError
_______ TestLLMModelAvailability.test_check_model_availability_available _______

self = <tests.test_llm.TestLLMModelAvailability testMethod=test_check_model_availability_available>

    def test_check_model_availability_available(self):
        """Test checking availability for an available model."""
        config = {"host": "localhost", "port": 11434, "model": "llama2"}
>       llm = LLM(LLMProvider.OLLAMA, config)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_llm.py:355: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <ticket_master_consolidated.LLM object at 0x10af459d0>
provider = <LLMProvider.OLLAMA: 'ollama'>
config = {'host': 'localhost', 'model': 'llama2', 'port': 11434}

    def __init__(self, provider: str, config: Dict[str, Any]) -> None:
        """Initialize LLM with specified provider and configuration."""
        self.provider = provider
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
        # Create appropriate backend
        if provider == "ollama":
            self.backend = OllamaBackend(config)
        else:
>           raise LLMError(f"Unsupported LLM provider: {provider}")
E           ticket_master_consolidated.LLMError: Unsupported LLM provider: LLMProvider.OLLAMA

src/ticket_master_consolidated.py:1781: LLMError
_____ TestLLMModelAvailability.test_check_model_availability_not_available _____

self = <tests.test_llm.TestLLMModelAvailability testMethod=test_check_model_availability_not_available>

    def test_check_model_availability_not_available(self):
        """Test checking availability for an unavailable model."""
        config = {"host": "localhost", "port": 11434, "model": "missing-model"}
>       llm = LLM(LLMProvider.OLLAMA, config)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_llm.py:373: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <ticket_master_consolidated.LLM object at 0x10af466f0>
provider = <LLMProvider.OLLAMA: 'ollama'>
config = {'host': 'localhost', 'model': 'missing-model', 'port': 11434}

    def __init__(self, provider: str, config: Dict[str, Any]) -> None:
        """Initialize LLM with specified provider and configuration."""
        self.provider = provider
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
        # Create appropriate backend
        if provider == "ollama":
            self.backend = OllamaBackend(config)
        else:
>           raise LLMError(f"Unsupported LLM provider: {provider}")
E           ticket_master_consolidated.LLMError: Unsupported LLM provider: LLMProvider.OLLAMA

src/ticket_master_consolidated.py:1781: LLMError
___ TestLLMModelAvailability.test_check_model_availability_with_auto_install ___

self = <tests.test_llm.TestLLMModelAvailability testMethod=test_check_model_availability_with_auto_install>

    def test_check_model_availability_with_auto_install(self):
        """Test model availability check with auto-install enabled."""
        config = {"host": "localhost", "port": 11434, "model": "test-model"}
>       llm = LLM(LLMProvider.OLLAMA, config)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_llm.py:390: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <ticket_master_consolidated.LLM object at 0x10af44e90>
provider = <LLMProvider.OLLAMA: 'ollama'>
config = {'host': 'localhost', 'model': 'test-model', 'port': 11434}

    def __init__(self, provider: str, config: Dict[str, Any]) -> None:
        """Initialize LLM with specified provider and configuration."""
        self.provider = provider
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
        # Create appropriate backend
        if provider == "ollama":
            self.backend = OllamaBackend(config)
        else:
>           raise LLMError(f"Unsupported LLM provider: {provider}")
E           ticket_master_consolidated.LLMError: Unsupported LLM provider: LLMProvider.OLLAMA

src/ticket_master_consolidated.py:1781: LLMError
_____________ TestLLMListModels.test_list_available_models_failure _____________

self = <tests.test_llm.TestLLMListModels testMethod=test_list_available_models_failure>

    def test_list_available_models_failure(self):
        """Test model listing failure."""
        config = {"host": "localhost", "port": 11434}
>       llm = LLM(LLMProvider.OLLAMA, config)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_llm.py:438: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <ticket_master_consolidated.LLM object at 0x10af44230>
provider = <LLMProvider.OLLAMA: 'ollama'>
config = {'host': 'localhost', 'port': 11434}

    def __init__(self, provider: str, config: Dict[str, Any]) -> None:
        """Initialize LLM with specified provider and configuration."""
        self.provider = provider
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
        # Create appropriate backend
        if provider == "ollama":
            self.backend = OllamaBackend(config)
        else:
>           raise LLMError(f"Unsupported LLM provider: {provider}")
E           ticket_master_consolidated.LLMError: Unsupported LLM provider: LLMProvider.OLLAMA

src/ticket_master_consolidated.py:1781: LLMError
_____________ TestLLMListModels.test_list_available_models_success _____________

self = <tests.test_llm.TestLLMListModels testMethod=test_list_available_models_success>

    def test_list_available_models_success(self):
        """Test successful model listing."""
        config = {"host": "localhost", "port": 11434}
>       llm = LLM(LLMProvider.OLLAMA, config)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_llm.py:416: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <ticket_master_consolidated.LLM object at 0x10ad12870>
provider = <LLMProvider.OLLAMA: 'ollama'>
config = {'host': 'localhost', 'port': 11434}

    def __init__(self, provider: str, config: Dict[str, Any]) -> None:
        """Initialize LLM with specified provider and configuration."""
        self.provider = provider
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
        # Create appropriate backend
        if provider == "ollama":
            self.backend = OllamaBackend(config)
        else:
>           raise LLMError(f"Unsupported LLM provider: {provider}")
E           ticket_master_consolidated.LLMError: Unsupported LLM provider: LLMProvider.OLLAMA

src/ticket_master_consolidated.py:1781: LLMError
______________ TestLLMBackendListing.test_list_available_backends ______________

self = <tests.test_llm.TestLLMBackendListing testMethod=test_list_available_backends>

    def test_list_available_backends(self):
        """Test listing available backends."""
        config = {"model": "test"}
>       llm = LLM(LLMProvider.OLLAMA, config)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_llm.py:461: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <ticket_master_consolidated.LLM object at 0x10af475c0>
provider = <LLMProvider.OLLAMA: 'ollama'>, config = {'model': 'test'}

    def __init__(self, provider: str, config: Dict[str, Any]) -> None:
        """Initialize LLM with specified provider and configuration."""
        self.provider = provider
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
        # Create appropriate backend
        if provider == "ollama":
            self.backend = OllamaBackend(config)
        else:
>           raise LLMError(f"Unsupported LLM provider: {provider}")
E           ticket_master_consolidated.LLMError: Unsupported LLM provider: LLMProvider.OLLAMA

src/ticket_master_consolidated.py:1781: LLMError
______ TestLLMBackendListing.test_list_available_backends_with_fallbacks _______

self = <tests.test_llm.TestLLMBackendListing testMethod=test_list_available_backends_with_fallbacks>

    def test_list_available_backends_with_fallbacks(self):
        """Test listing backends with fallbacks configured."""
        config = {"model": "test"}
        fallback_configs = [
            {"provider": "mock", "model": "mock-model"},
            {"provider": "openai", "api_key": "test-key", "model": "gpt-4"},
        ]
    
>       llm = LLM(LLMProvider.OLLAMA, config, fallback_configs)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: LLM.__init__() takes 3 positional arguments but 4 were given

tests/test_llm.py:480: TypeError
___________ TestLLMFailureScenarios.test_generate_all_backends_fail ____________

self = <tests.test_llm.TestLLMFailureScenarios testMethod=test_generate_all_backends_fail>

    def test_generate_all_backends_fail(self):
        """Test generation when all backends fail."""
        config = {"model": "test"}
        fallback_configs = [{"provider": "mock", "model": "mock-model"}]
    
>       llm = LLM(LLMProvider.OLLAMA, config, fallback_configs)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: LLM.__init__() takes 3 positional arguments but 4 were given

tests/test_llm.py:524: TypeError
___________ TestLLMFailureScenarios.test_generate_validation_failure ___________

self = <tests.test_llm.TestLLMFailureScenarios testMethod=test_generate_validation_failure>

    def test_generate_validation_failure(self):
        """Test response validation identifying poor quality responses."""
        config = {"model": "test"}
>       llm = LLM(LLMProvider.MOCK, config)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_llm.py:561: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <ticket_master_consolidated.LLM object at 0x10aeba840>
provider = <LLMProvider.MOCK: 'mock'>, config = {'model': 'test'}

    def __init__(self, provider: str, config: Dict[str, Any]) -> None:
        """Initialize LLM with specified provider and configuration."""
        self.provider = provider
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
        # Create appropriate backend
        if provider == "ollama":
            self.backend = OllamaBackend(config)
        else:
>           raise LLMError(f"Unsupported LLM provider: {provider}")
E           ticket_master_consolidated.LLMError: Unsupported LLM provider: LLMProvider.MOCK

src/ticket_master_consolidated.py:1781: LLMError
_ TestLLMFailureScenarios.test_generate_with_primary_failure_fallback_success __

self = <tests.test_llm.TestLLMFailureScenarios testMethod=test_generate_with_primary_failure_fallback_success>

    def test_generate_with_primary_failure_fallback_success(self):
        """Test generation with primary backend failing but fallback succeeding."""
        config = {"model": "test"}
        fallback_configs = [{"provider": "mock", "model": "mock-model"}]
    
>       llm = LLM(LLMProvider.OLLAMA, config, fallback_configs)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: LLM.__init__() takes 3 positional arguments but 4 were given

tests/test_llm.py:498: TypeError
______________ TestLLMFailureScenarios.test_generate_with_retries ______________

self = <tests.test_llm.TestLLMFailureScenarios testMethod=test_generate_with_retries>

    def test_generate_with_retries(self):
        """Test generation with retries before success."""
        config = {"model": "test"}
>       llm = LLM(LLMProvider.OLLAMA, config)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_llm.py:542: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <ticket_master_consolidated.LLM object at 0x10aeb81a0>
provider = <LLMProvider.OLLAMA: 'ollama'>, config = {'model': 'test'}

    def __init__(self, provider: str, config: Dict[str, Any]) -> None:
        """Initialize LLM with specified provider and configuration."""
        self.provider = provider
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
        # Create appropriate backend
        if provider == "ollama":
            self.backend = OllamaBackend(config)
        else:
>           raise LLMError(f"Unsupported LLM provider: {provider}")
E           ticket_master_consolidated.LLMError: Unsupported LLM provider: LLMProvider.OLLAMA

src/ticket_master_consolidated.py:1781: LLMError
_______ TestLLMFailureScenarios.test_response_validation_empty_response ________

self = <tests.test_llm.TestLLMFailureScenarios testMethod=test_response_validation_empty_response>

    def test_response_validation_empty_response(self):
        """Test validation of empty responses."""
        config = {"model": "test"}
>       llm = LLM(LLMProvider.MOCK, config)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_llm.py:573: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <ticket_master_consolidated.LLM object at 0x10aebb050>
provider = <LLMProvider.MOCK: 'mock'>, config = {'model': 'test'}

    def __init__(self, provider: str, config: Dict[str, Any]) -> None:
        """Initialize LLM with specified provider and configuration."""
        self.provider = provider
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
        # Create appropriate backend
        if provider == "ollama":
            self.backend = OllamaBackend(config)
        else:
>           raise LLMError(f"Unsupported LLM provider: {provider}")
E           ticket_master_consolidated.LLMError: Unsupported LLM provider: LLMProvider.MOCK

src/ticket_master_consolidated.py:1781: LLMError
_______ TestLLMFailureScenarios.test_response_validation_error_patterns ________

self = <tests.test_llm.TestLLMFailureScenarios testMethod=test_response_validation_error_patterns>

    def test_response_validation_error_patterns(self):
        """Test validation detecting common error patterns."""
        config = {"model": "test"}
>       llm = LLM(LLMProvider.MOCK, config)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_llm.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <ticket_master_consolidated.LLM object at 0x10af45f40>
provider = <LLMProvider.MOCK: 'mock'>, config = {'model': 'test'}

    def __init__(self, provider: str, config: Dict[str, Any]) -> None:
        """Initialize LLM with specified provider and configuration."""
        self.provider = provider
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
        # Create appropriate backend
        if provider == "ollama":
            self.backend = OllamaBackend(config)
        else:
>           raise LLMError(f"Unsupported LLM provider: {provider}")
E           ticket_master_consolidated.LLMError: Unsupported LLM provider: LLMProvider.MOCK

src/ticket_master_consolidated.py:1781: LLMError
_____ TestLLMFailureScenarios.test_response_validation_repetitive_content ______

self = <tests.test_llm.TestLLMFailureScenarios testMethod=test_response_validation_repetitive_content>

    def test_response_validation_repetitive_content(self):
        """Test validation of repetitive content."""
        config = {"model": "test"}
>       llm = LLM(LLMProvider.MOCK, config)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_llm.py:585: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <ticket_master_consolidated.LLM object at 0x10aac9190>
provider = <LLMProvider.MOCK: 'mock'>, config = {'model': 'test'}

    def __init__(self, provider: str, config: Dict[str, Any]) -> None:
        """Initialize LLM with specified provider and configuration."""
        self.provider = provider
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
        # Create appropriate backend
        if provider == "ollama":
            self.backend = OllamaBackend(config)
        else:
>           raise LLMError(f"Unsupported LLM provider: {provider}")
E           ticket_master_consolidated.LLMError: Unsupported LLM provider: LLMProvider.MOCK

src/ticket_master_consolidated.py:1781: LLMError
__________ TestOpenAIIntegration.test_openai_backend_custom_base_url ___________

self = <tests.test_llm.TestOpenAIIntegration testMethod=test_openai_backend_custom_base_url>

    def test_openai_backend_custom_base_url(self):
        """Test OpenAI backend with custom base URL."""
        config = {
            "api_key": "test-key",
            "model": "gpt-4",
            "base_url": "https://custom.openai.proxy.com/v1",
        }
    
        backend = OpenAIBackend(config)
    
        self.assertEqual(
>           backend.base_url, "https://custom.openai.proxy.com/v1"
            ^^^^^^^^^^^^^^^^
        )
E       AttributeError: 'OpenAIBackend' object has no attribute 'base_url'

tests/test_llm.py:633: AttributeError
___________ TestOpenAIIntegration.test_openai_backend_initialization ___________

self = <tests.test_llm.TestOpenAIIntegration testMethod=test_openai_backend_initialization>

    def test_openai_backend_initialization(self):
        """Test OpenAI backend initialization with API key."""
        config = {"api_key": "test-api-key", "model": "gpt-4"}
    
        backend = OpenAIBackend(config)
    
        self.assertEqual(backend.api_key, "test-api-key")
        self.assertEqual(backend.model, "gpt-4")
>       self.assertEqual(backend.base_url, "https://api.openai.com/v1")
                         ^^^^^^^^^^^^^^^^
E       AttributeError: 'OpenAIBackend' object has no attribute 'base_url'

tests/test_llm.py:620: AttributeError
______________ TestOpenAIIntegration.test_openai_generate_success ______________

self = <tests.test_llm.TestOpenAIIntegration testMethod=test_openai_generate_success>
mock_post = <MagicMock name='post' id='4478181376'>

    @patch("ticket_master_consolidated.requests.post")
    def test_openai_generate_success(self, mock_post):
        """Test successful OpenAI text generation."""
        config = {"api_key": "test-key", "model": "gpt-4"}
        backend = OpenAIBackend(config)
    
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Generated text response"}}]
        }
        mock_post.return_value = mock_response
    
>       result = backend.generate("Test prompt")
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_llm.py:649: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <ticket_master_consolidated.OpenAIBackend object at 0x10aeba990>
prompt = 'Test prompt', kwargs = {}

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using OpenAI."""
>       raise LLMProviderError("OpenAI backend not fully implemented")
E       ticket_master_consolidated.LLMProviderError: OpenAI backend not fully implemented

src/ticket_master_consolidated.py:1753: LLMProviderError
____________ TestOpenAIIntegration.test_openai_is_available_success ____________

self = <tests.test_llm.TestOpenAIIntegration testMethod=test_openai_is_available_success>
mock_get = <MagicMock name='get' id='4473515392'>

    @patch("ticket_master_consolidated.requests.get")
    def test_openai_is_available_success(self, mock_get):
        """Test OpenAI availability check success."""
        config = {"api_key": "test-key", "model": "gpt-4"}
        backend = OpenAIBackend(config)
    
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
    
>       self.assertTrue(backend.is_available())
E       AssertionError: False is not true

tests/test_llm.py:681: AssertionError
__________ TestGenerateSampleIssues.test_generate_sample_issues_basic __________

self = <tests.test_main.TestGenerateSampleIssues testMethod=test_generate_sample_issues_basic>

    def test_generate_sample_issues_basic(self):
        """Test basic issue generation."""
        issues = main.generate_sample_issues(self.analysis, self.config)
    
        self.assertIsInstance(issues, list)
        self.assertLessEqual(
            len(issues), self.config["issue_generation"]["max_issues"]
        )
    
        # Check that issues are Issue objects
        for issue in issues:
>           self.assertIsInstance(issue, main.Issue)
E           TypeError: isinstance() arg 2 must be a type, a tuple of types, or a union

tests/test_main.py:129: TypeError
----------------------------- Captured stdout call -----------------------------
2025-09-30 00:00:12 - main - INFO - Generated 4 sample issues
2025-09-30 00:00:12 - main - INFO - Generated 4 sample issues
2025-09-30 00:00:12 - main - INFO - Generated 4 sample issues
------------------------------ Captured log call -------------------------------
INFO     main:main.py:655 Generated 4 sample issues
_____ TestValidateConfigCommand.test_validate_config_command_valid_config ______

self = <tests.test_main.TestValidateConfigCommand testMethod=test_validate_config_command_valid_config>
mock_print = <MagicMock name='print' id='4475122608'>
mock_load_config = <MagicMock name='load_config' id='4479050064'>

    @patch("main.load_config")
    @patch("builtins.print")
    def test_validate_config_command_valid_config(
        self, mock_print, mock_load_config
    ):
        """Test validate_config_command with valid configuration."""
        mock_load_config.return_value = {
            "github": {"token": "test_token"},
            "issue_generation": {"max_issues": 5},
        }
    
        result = main.validate_config_command()
    
>       self.assertEqual(result, 0)
E       AssertionError: 1 != 0

tests/test_main.py:305: AssertionError
----------------------------- Captured stdout call -----------------------------
2025-09-30 00:00:12 - main - INFO - Validating configuration...
2025-09-30 00:00:12 - main - INFO - Validating configuration...
2025-09-30 00:00:12 - main - INFO - Validating configuration...
------------------------------ Captured log call -------------------------------
INFO     main:main.py:876 Validating configuration...
_______ TestValidateConfigCommand.test_validate_config_command_with_path _______

self = <tests.test_main.TestValidateConfigCommand testMethod=test_validate_config_command_with_path>
mock_print = <MagicMock name='print' id='4478305776'>
mock_load_config = <MagicMock name='load_config' id='4478304864'>

    @patch("main.load_config")
    @patch("builtins.print")
    def test_validate_config_command_with_path(
        self, mock_print, mock_load_config
    ):
        """Test validate_config_command with specific config path."""
        mock_load_config.return_value = {
            "github": {"token": "test_token"},
            "issue_generation": {"max_issues": 5},
        }
    
        result = main.validate_config_command("/path/to/config.yaml")
    
>       self.assertEqual(result, 0)
E       AssertionError: 1 != 0

tests/test_main.py:322: AssertionError
----------------------------- Captured stdout call -----------------------------
2025-09-30 00:00:12 - main - INFO - Validating configuration...
2025-09-30 00:00:12 - main - INFO - Validating configuration...
2025-09-30 00:00:12 - main - INFO - Validating configuration...
------------------------------ Captured log call -------------------------------
INFO     main:main.py:876 Validating configuration...
____________ TestAnalyzeRepository.test_analyze_repository_success _____________

repo_path = '/path/to/repo', config = {'repository': {'max_commits': 100}}

    def analyze_repository(
        repo_path: str, config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze repository and prepare data for issue generation.
    
        Args:
            repo_path: Path to Git repository
            config: Configuration dictionary
    
        Returns:
            Dictionary containing repository analysis results
    
        Raises:
            RepositoryError: If repository analysis fails
        """
        logger = logging.getLogger(__name__)
    
        try:
            # Initialize repository
            repo = Repository(repo_path)
            logger.info(f"Analyzing repository: {repo.path}")
    
            # Get repository information
            repo_info = repo.get_repository_info()
            logger.info(
>               f"Repository: {repo_info['name']} ({repo_info['active_branch']})"
                               ^^^^^^^^^^^^^^^^^
            )
E           TypeError: 'Mock' object is not subscriptable

main.py:166: TypeError

During handling of the above exception, another exception occurred:

self = <tests.test_main.TestAnalyzeRepository testMethod=test_analyze_repository_success>
mock_repository = <MagicMock name='Repository' id='4478316336'>

    @patch("main.Repository")
    def test_analyze_repository_success(self, mock_repository):
        """Test successful repository analysis."""
        mock_repo_instance = Mock()
        mock_repo_instance.analyze.return_value = {
            "commits": [],
            "file_changes": {"new_files": [], "modified_files": {}},
            "summary": {"commit_count": 0},
        }
        mock_repository.return_value = mock_repo_instance
    
        config = {"repository": {"max_commits": 100}}
>       result = main.analyze_repository("/path/to/repo", config)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_main.py:358: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

repo_path = '/path/to/repo', config = {'repository': {'max_commits': 100}}

    def analyze_repository(
        repo_path: str, config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze repository and prepare data for issue generation.
    
        Args:
            repo_path: Path to Git repository
            config: Configuration dictionary
    
        Returns:
            Dictionary containing repository analysis results
    
        Raises:
            RepositoryError: If repository analysis fails
        """
        logger = logging.getLogger(__name__)
    
        try:
            # Initialize repository
            repo = Repository(repo_path)
            logger.info(f"Analyzing repository: {repo.path}")
    
            # Get repository information
            repo_info = repo.get_repository_info()
            logger.info(
                f"Repository: {repo_info['name']} ({repo_info['active_branch']})"
            )
    
            # Try to get commit history, but fall back to minimal analysis if it fails
            max_commits = config["repository"]["max_commits"]
            try:
                commits = repo.get_commit_history(max_count=max_commits)
                logger.info(f"Retrieved {len(commits)} commits")
            except Exception as commit_error:
                logger.warning(
                    f"Could not get detailed commit history: {commit_error}"
                )
                logger.info("Using minimal commit analysis")
                commits = [
                    {
                        "hash": "unknown",
                        "short_hash": "unknown",
                        "author": {"name": "unknown", "email": "unknown"},
                        "committer": {"name": "unknown", "email": "unknown"},
                        "message": "Repository analysis limited due to git issues",
                        "summary": "Limited analysis mode",
                        "date": datetime.now(),
                        "files_changed": 0,
                        "insertions": 0,
                        "deletions": 0,
                    }
                ]
    
            # Try to get file changes, but fall back to minimal analysis if it fails
            try:
                file_changes = repo.get_file_changes(max_commits=max_commits)
                logger.info(
                    f"Analyzed changes across "
                    f"{file_changes['summary']['total_files']} files"
                )
            except Exception as file_error:
                logger.warning(
                    f"Could not get detailed file changes: {file_error}"
                )
                logger.info("Using minimal file change analysis")
                file_changes = {
                    "modified_files": {},
                    "new_files": [],
                    "deleted_files": [],
                    "renamed_files": [],
                    "summary": {
                        "total_files": 1,
                        "total_insertions": 0,
                        "total_deletions": 0,
                    },
                }
    
            return {
                "repository_info": repo_info,
                "commits": commits,
                "file_changes": file_changes,
                "analysis_summary": {
                    "commit_count": len(commits),
                    "files_modified": len(file_changes["modified_files"]),
                    "files_added": len(file_changes["new_files"]),
                    "files_deleted": len(file_changes["deleted_files"]),
                    "total_insertions": file_changes["summary"][
                        "total_insertions"
                    ],
                    "total_deletions": file_changes["summary"]["total_deletions"],
                },
            }
    
        except Exception as e:
>           raise RepositoryError(f"Repository analysis failed: {e}")
E           ticket_master_consolidated.RepositoryError: Repository analysis failed: 'Mock' object is not subscriptable

main.py:235: RepositoryError
----------------------------- Captured stdout call -----------------------------
2025-09-30 00:00:12 - main - INFO - Analyzing repository: <Mock name='Repository().path' id='4477635808'>
2025-09-30 00:00:12 - main - INFO - Analyzing repository: <Mock name='Repository().path' id='4477635808'>
2025-09-30 00:00:12 - main - INFO - Analyzing repository: <Mock name='Repository().path' id='4477635808'>
------------------------------ Captured log call -------------------------------
INFO     main:main.py:161 Analyzing repository: <Mock name='Repository().path' id='4477635808'>
_______ TestGenerateIssuesWithLLM.test_generate_issues_with_llm_fallback _______

self = <tests.test_main.TestGenerateIssuesWithLLM testMethod=test_generate_issues_with_llm_fallback>
mock_generate_standard = <MagicMock name='generate_issues_with_standard_llm' id='4476980160'>
mock_generate_sample = <MagicMock name='generate_sample_issues' id='4476987744'>

    @patch("main.generate_sample_issues")
    @patch("main.generate_issues_with_standard_llm")
    def test_generate_issues_with_llm_fallback(
        self, mock_generate_standard, mock_generate_sample
    ):
        """Test LLM issue generation fallback to samples."""
        config = {"llm": {"provider": "ollama"}}
        mock_generate_standard.side_effect = Exception("LLM error")
    
        mock_issue = Mock()
        mock_issue.title = "Sample Issue"
        mock_generate_sample.return_value = [mock_issue]
    
        result = main.generate_issues_with_llm(self.analysis, config)
    
        self.assertEqual(len(result), 1)
>       mock_generate_standard.assert_called_once()

tests/test_main.py:415: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <MagicMock name='generate_issues_with_standard_llm' id='4476980160'>

    def assert_called_once(self):
        """assert that the mock was called only once.
        """
        if not self.call_count == 1:
            msg = ("Expected '%s' to have been called once. Called %s times.%s"
                   % (self._mock_name or 'mock',
                      self.call_count,
                      self._calls_repr()))
>           raise AssertionError(msg)
E           AssertionError: Expected 'generate_issues_with_standard_llm' to have been called once. Called 0 times.

/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:928: AssertionError
----------------------------- Captured stdout call -----------------------------
2025-09-30 00:00:12 - main - ERROR - Unexpected error in LLM issue generation: 'issue_generation'
2025-09-30 00:00:12 - main - ERROR - Unexpected error in LLM issue generation: 'issue_generation'
2025-09-30 00:00:12 - main - ERROR - Unexpected error in LLM issue generation: 'issue_generation'
2025-09-30 00:00:12 - main - INFO - Falling back to sample issue generation
2025-09-30 00:00:12 - main - INFO - Falling back to sample issue generation
2025-09-30 00:00:12 - main - INFO - Falling back to sample issue generation
------------------------------ Captured log call -------------------------------
ERROR    main:main.py:328 Unexpected error in LLM issue generation: 'issue_generation'
INFO     main:main.py:329 Falling back to sample issue generation
_______ TestGenerateIssuesWithLLM.test_generate_issues_with_llm_success ________

analysis = {'commits': [], 'file_changes': {'modified_files': {}, 'new_files': []}, 'summary': {'commit_count': 0}}
config = {'llm': {'provider': 'ollama'}}

    def generate_issues_with_llm(
        analysis: Dict[str, Any], config: Dict[str, Any]
    ) -> List[Issue]:
        """Generate issues using LLM based on repository analysis.
    
        Args:
            analysis: Repository analysis results
            config: Configuration dictionary
    
        Returns:
            List of generated Issue objects
        """
        logger = logging.getLogger(__name__)
        issues = []
    
        try:
            # Get max issues from config
>           max_issues = config["issue_generation"]["max_issues"]
                         ^^^^^^^^^^^^^^^^^^^^^^^^^^
E           KeyError: 'issue_generation'

main.py:255: KeyError

During handling of the above exception, another exception occurred:

self = <tests.test_main.TestGenerateIssuesWithLLM testMethod=test_generate_issues_with_llm_success>
mock_generate_standard = <MagicMock name='generate_issues_with_standard_llm' id='4476988848'>

    @patch("main.generate_issues_with_standard_llm")
    def test_generate_issues_with_llm_success(self, mock_generate_standard):
        """Test successful LLM issue generation."""
        config = {"llm": {"provider": "ollama"}}
        mock_issue = Mock()
        mock_issue.title = "Test Issue"
        mock_generate_standard.return_value = [mock_issue]
    
>       result = main.generate_issues_with_llm(self.analysis, config)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_main.py:394: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
main.py:330: in generate_issues_with_llm
    return generate_sample_issues(analysis, config)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

analysis = {'commits': [], 'file_changes': {'modified_files': {}, 'new_files': []}, 'summary': {'commit_count': 0}}
config = {'llm': {'provider': 'ollama'}}

    def generate_sample_issues(
        analysis: Dict[str, Any], config: Dict[str, Any]
    ) -> List[Issue]:
        """Generate sample issues based on repository analysis.
    
        This is a fallback implementation that generates basic issues based on
        repository patterns when LLM is not available.
    
        Args:
            analysis: Repository analysis results
            config: Configuration dictionary
    
        Returns:
            List of generated Issue objects
        """
        logger = logging.getLogger(__name__)
        issues = []
    
        commits = analysis["commits"]
        file_changes = analysis["file_changes"]
>       summary = analysis["analysis_summary"]
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       KeyError: 'analysis_summary'

main.py:520: KeyError
----------------------------- Captured stdout call -----------------------------
2025-09-30 00:00:12 - main - ERROR - Unexpected error in LLM issue generation: 'issue_generation'
2025-09-30 00:00:12 - main - ERROR - Unexpected error in LLM issue generation: 'issue_generation'
2025-09-30 00:00:12 - main - ERROR - Unexpected error in LLM issue generation: 'issue_generation'
2025-09-30 00:00:12 - main - INFO - Falling back to sample issue generation
2025-09-30 00:00:12 - main - INFO - Falling back to sample issue generation
2025-09-30 00:00:12 - main - INFO - Falling back to sample issue generation
------------------------------ Captured log call -------------------------------
ERROR    main:main.py:328 Unexpected error in LLM issue generation: 'issue_generation'
INFO     main:main.py:329 Falling back to sample issue generation
________ TestCreateIssuesOnGitHub.test_create_issues_on_github_dry_run _________

self = <tests.test_main.TestCreateIssuesOnGitHub testMethod=test_create_issues_on_github_dry_run>
mock_issue_class = <MagicMock name='Issue' id='4475577952'>

    @patch("main.Issue")
    def test_create_issues_on_github_dry_run(self, mock_issue_class):
        """Test creating issues in dry run mode."""
        config = {"github": {"token": "test_token"}}
        issues = [self.mock_issue]
    
        results = main.create_issues_on_github(
            issues, "test/repo", config, dry_run=True
        )
    
        self.assertEqual(len(results), 1)
>       self.assertTrue(results[0]["dry_run"])
                        ^^^^^^^^^^^^^^^^^^^^^
E       KeyError: 'dry_run'

tests/test_main.py:440: KeyError
----------------------------- Captured stdout call -----------------------------
2025-09-30 00:00:12 - main - INFO - DRY RUN MODE: Issues will be validated but not created
2025-09-30 00:00:12 - main - INFO - DRY RUN MODE: Issues will be validated but not created
2025-09-30 00:00:12 - main - INFO - DRY RUN MODE: Issues will be validated but not created
2025-09-30 00:00:12 - main - INFO - Skipping GitHub connection test in dry-run mode
2025-09-30 00:00:12 - main - INFO - Skipping GitHub connection test in dry-run mode
2025-09-30 00:00:12 - main - INFO - Skipping GitHub connection test in dry-run mode
2025-09-30 00:00:12 - main - ERROR - Failed to create issue 1: can only join an iterable
2025-09-30 00:00:12 - main - ERROR - Failed to create issue 1: can only join an iterable
2025-09-30 00:00:12 - main - ERROR - Failed to create issue 1: can only join an iterable
------------------------------ Captured log call -------------------------------
INFO     main:main.py:684 DRY RUN MODE: Issues will be validated but not created
INFO     main:main.py:710 Skipping GitHub connection test in dry-run mode
ERROR    main:main.py:761 Failed to create issue 1: can only join an iterable
________ TestCreateIssuesOnGitHub.test_create_issues_on_github_failure _________

issues = [<Mock id='4472818384'>], repo_name = 'test/repo'
config = {'github': {'token': 'test_token'}}, dry_run = False

    def create_issues_on_github(
        issues: List[Issue],
        repo_name: str,
        config: Dict[str, Any],
        dry_run: bool = True,
    ) -> List[Dict[str, Any]]:
        """Create issues on GitHub.
    
        Args:
            issues: List of Issue objects to create
            repo_name: GitHub repository name (owner/repo)
            config: Configuration dictionary
            dry_run: If True, validate but don't actually create issues
    
        Returns:
            List of dictionaries containing creation results
    
        Raises:
            GitHubAuthError: If GitHub authentication fails
            IssueError: If issue creation fails
        """
        logger = logging.getLogger(__name__)
        results = []
    
        if dry_run:
            logger.info("DRY RUN MODE: Issues will be validated but not created")
    
        # Test GitHub connection first (skip if using dummy token or dry run)
        github_token = config["github"]["token"]
        if not dry_run and github_token and github_token != "dummy_token":
            try:
                from ticket_master_consolidated import test_github_connection
    
                connection_test = test_github_connection(github_token)
    
                if not connection_test["authenticated"]:
>                   raise GitHubAuthError(
                        f"GitHub authentication failed: {connection_test['error']}"
                    )
E                   ticket_master_consolidated.GitHubAuthError: GitHub authentication failed: Invalid GitHub credentials: 401 {"message": "Bad credentials", "documentation_url": "https://docs.github.com/rest", "status": "401"}

main.py:695: GitHubAuthError

During handling of the above exception, another exception occurred:

self = <tests.test_main.TestCreateIssuesOnGitHub testMethod=test_create_issues_on_github_failure>
mock_issue_class = <MagicMock name='Issue' id='4472826160'>

    @patch("main.Issue")
    def test_create_issues_on_github_failure(self, mock_issue_class):
        """Test issue creation failure."""
        config = {"github": {"token": "test_token"}}
        issues = [self.mock_issue]
    
        mock_github_issue = Mock()
        mock_github_issue.create_issue.side_effect = Exception(
            "Creation failed"
        )
        mock_issue_class.return_value = mock_github_issue
    
>       results = main.create_issues_on_github(
            issues, "test/repo", config, dry_run=False
        )

tests/test_main.py:479: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

issues = [<Mock id='4472818384'>], repo_name = 'test/repo'
config = {'github': {'token': 'test_token'}}, dry_run = False

    def create_issues_on_github(
        issues: List[Issue],
        repo_name: str,
        config: Dict[str, Any],
        dry_run: bool = True,
    ) -> List[Dict[str, Any]]:
        """Create issues on GitHub.
    
        Args:
            issues: List of Issue objects to create
            repo_name: GitHub repository name (owner/repo)
            config: Configuration dictionary
            dry_run: If True, validate but don't actually create issues
    
        Returns:
            List of dictionaries containing creation results
    
        Raises:
            GitHubAuthError: If GitHub authentication fails
            IssueError: If issue creation fails
        """
        logger = logging.getLogger(__name__)
        results = []
    
        if dry_run:
            logger.info("DRY RUN MODE: Issues will be validated but not created")
    
        # Test GitHub connection first (skip if using dummy token or dry run)
        github_token = config["github"]["token"]
        if not dry_run and github_token and github_token != "dummy_token":
            try:
                from ticket_master_consolidated import test_github_connection
    
                connection_test = test_github_connection(github_token)
    
                if not connection_test["authenticated"]:
                    raise GitHubAuthError(
                        f"GitHub authentication failed: {connection_test['error']}"
                    )
    
                logger.info(
                    f"Connected to GitHub as: {connection_test['user']['login']}"
                )
                logger.info(
                    f"Rate limit remaining: {connection_test['rate_limit']['core']['remaining']}"
                )
    
            except Exception as e:
>               raise GitHubAuthError(f"Failed to connect to GitHub: {e}")
E               ticket_master_consolidated.GitHubAuthError: Failed to connect to GitHub: GitHub authentication failed: Invalid GitHub credentials: 401 {"message": "Bad credentials", "documentation_url": "https://docs.github.com/rest", "status": "401"}

main.py:707: GitHubAuthError
________ TestCreateIssuesOnGitHub.test_create_issues_on_github_success _________

issues = [<Mock id='4476988944'>], repo_name = 'test/repo'
config = {'github': {'token': 'test_token'}}, dry_run = False

    def create_issues_on_github(
        issues: List[Issue],
        repo_name: str,
        config: Dict[str, Any],
        dry_run: bool = True,
    ) -> List[Dict[str, Any]]:
        """Create issues on GitHub.
    
        Args:
            issues: List of Issue objects to create
            repo_name: GitHub repository name (owner/repo)
            config: Configuration dictionary
            dry_run: If True, validate but don't actually create issues
    
        Returns:
            List of dictionaries containing creation results
    
        Raises:
            GitHubAuthError: If GitHub authentication fails
            IssueError: If issue creation fails
        """
        logger = logging.getLogger(__name__)
        results = []
    
        if dry_run:
            logger.info("DRY RUN MODE: Issues will be validated but not created")
    
        # Test GitHub connection first (skip if using dummy token or dry run)
        github_token = config["github"]["token"]
        if not dry_run and github_token and github_token != "dummy_token":
            try:
                from ticket_master_consolidated import test_github_connection
    
                connection_test = test_github_connection(github_token)
    
                if not connection_test["authenticated"]:
>                   raise GitHubAuthError(
                        f"GitHub authentication failed: {connection_test['error']}"
                    )
E                   ticket_master_consolidated.GitHubAuthError: GitHub authentication failed: Invalid GitHub credentials: 401 {"message": "Bad credentials", "documentation_url": "https://docs.github.com/rest", "status": "401"}

main.py:695: GitHubAuthError

During handling of the above exception, another exception occurred:

self = <tests.test_main.TestCreateIssuesOnGitHub testMethod=test_create_issues_on_github_success>
mock_issue_class = <MagicMock name='Issue' id='4476991152'>

    @patch("main.Issue")
    def test_create_issues_on_github_success(self, mock_issue_class):
        """Test successful issue creation."""
        config = {"github": {"token": "test_token"}}
        issues = [self.mock_issue]
    
        mock_github_issue = Mock()
        mock_github_issue.create_issue.return_value = {
            "number": 123,
            "html_url": "https://github.com/test/repo/issues/123",
        }
        mock_issue_class.return_value = mock_github_issue
    
>       results = main.create_issues_on_github(
            issues, "test/repo", config, dry_run=False
        )

tests/test_main.py:458: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

issues = [<Mock id='4476988944'>], repo_name = 'test/repo'
config = {'github': {'token': 'test_token'}}, dry_run = False

    def create_issues_on_github(
        issues: List[Issue],
        repo_name: str,
        config: Dict[str, Any],
        dry_run: bool = True,
    ) -> List[Dict[str, Any]]:
        """Create issues on GitHub.
    
        Args:
            issues: List of Issue objects to create
            repo_name: GitHub repository name (owner/repo)
            config: Configuration dictionary
            dry_run: If True, validate but don't actually create issues
    
        Returns:
            List of dictionaries containing creation results
    
        Raises:
            GitHubAuthError: If GitHub authentication fails
            IssueError: If issue creation fails
        """
        logger = logging.getLogger(__name__)
        results = []
    
        if dry_run:
            logger.info("DRY RUN MODE: Issues will be validated but not created")
    
        # Test GitHub connection first (skip if using dummy token or dry run)
        github_token = config["github"]["token"]
        if not dry_run and github_token and github_token != "dummy_token":
            try:
                from ticket_master_consolidated import test_github_connection
    
                connection_test = test_github_connection(github_token)
    
                if not connection_test["authenticated"]:
                    raise GitHubAuthError(
                        f"GitHub authentication failed: {connection_test['error']}"
                    )
    
                logger.info(
                    f"Connected to GitHub as: {connection_test['user']['login']}"
                )
                logger.info(
                    f"Rate limit remaining: {connection_test['rate_limit']['core']['remaining']}"
                )
    
            except Exception as e:
>               raise GitHubAuthError(f"Failed to connect to GitHub: {e}")
E               ticket_master_consolidated.GitHubAuthError: Failed to connect to GitHub: GitHub authentication failed: Invalid GitHub credentials: 401 {"message": "Bad credentials", "documentation_url": "https://docs.github.com/rest", "status": "401"}

main.py:707: GitHubAuthError
_________________ TestUserDatabase.test_cache_repository_data __________________

self = <tests.test_new_classes.TestUserDatabase testMethod=test_cache_repository_data>

    def test_cache_repository_data(self):
        """Test repository data caching."""
>       with self.db:
             ^^^^^^^
E       TypeError: 'UserDatabase' object does not support the context manager protocol

tests/test_new_classes.py:95: TypeError
----------------------------- Captured stdout call -----------------------------
2025-09-30 00:00:13 - UserDatabase - INFO - Database initialized at /var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmp78miffsr/test.db
2025-09-30 00:00:13 - UserDatabase - INFO - Database initialized at /var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmp78miffsr/test.db
2025-09-30 00:00:13 - UserDatabase - INFO - Database initialized at /var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmp78miffsr/test.db
------------------------------ Captured log call -------------------------------
INFO     UserDatabase:ticket_master_consolidated.py:2200 Database initialized at /var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmp78miffsr/test.db
___________________ TestUserDatabase.test_connect_disconnect ___________________

self = <tests.test_new_classes.TestUserDatabase testMethod=test_connect_disconnect>

    def test_connect_disconnect(self):
        """Test database connection and disconnection."""
>       self.assertFalse(self.db.is_connected())
E       AssertionError: True is not false

tests/test_new_classes.py:57: AssertionError
----------------------------- Captured stdout call -----------------------------
2025-09-30 00:00:13 - UserDatabase - INFO - Database initialized at /var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmpmbv9n4mo/test.db
2025-09-30 00:00:13 - UserDatabase - INFO - Database initialized at /var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmpmbv9n4mo/test.db
2025-09-30 00:00:13 - UserDatabase - INFO - Database initialized at /var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmpmbv9n4mo/test.db
------------------------------ Captured log call -------------------------------
INFO     UserDatabase:ticket_master_consolidated.py:2200 Database initialized at /var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmpmbv9n4mo/test.db
____________________ TestUserDatabase.test_context_manager _____________________

self = <tests.test_new_classes.TestUserDatabase testMethod=test_context_manager>

    def test_context_manager(self):
        """Test database context manager."""
>       with self.db as db:
             ^^^^^^^
E       TypeError: 'UserDatabase' object does not support the context manager protocol

tests/test_new_classes.py:67: TypeError
----------------------------- Captured stdout call -----------------------------
2025-09-30 00:00:13 - UserDatabase - INFO - Database initialized at /var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmpfe6yn2gm/test.db
2025-09-30 00:00:13 - UserDatabase - INFO - Database initialized at /var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmpfe6yn2gm/test.db
2025-09-30 00:00:13 - UserDatabase - INFO - Database initialized at /var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmpfe6yn2gm/test.db
------------------------------ Captured log call -------------------------------
INFO     UserDatabase:ticket_master_consolidated.py:2200 Database initialized at /var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmpfe6yn2gm/test.db
_____________________ TestUserDatabase.test_create_tables ______________________

self = <tests.test_new_classes.TestUserDatabase testMethod=test_create_tables>

    def test_create_tables(self):
        """Test table creation."""
>       with self.db:
             ^^^^^^^
E       TypeError: 'UserDatabase' object does not support the context manager protocol

tests/test_new_classes.py:73: TypeError
----------------------------- Captured stdout call -----------------------------
2025-09-30 00:00:13 - UserDatabase - INFO - Database initialized at /var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmpxy1mzdu3/test.db
2025-09-30 00:00:13 - UserDatabase - INFO - Database initialized at /var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmpxy1mzdu3/test.db
2025-09-30 00:00:13 - UserDatabase - INFO - Database initialized at /var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmpxy1mzdu3/test.db
------------------------------ Captured log call -------------------------------
INFO     UserDatabase:ticket_master_consolidated.py:2200 Database initialized at /var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmpxy1mzdu3/test.db
____________________ TestUserDatabase.test_user_preferences ____________________

self = <tests.test_new_classes.TestUserDatabase testMethod=test_user_preferences>

    def test_user_preferences(self):
        """Test user preference storage and retrieval."""
>       with self.db:
             ^^^^^^^
E       TypeError: 'UserDatabase' object does not support the context manager protocol

tests/test_new_classes.py:79: TypeError
----------------------------- Captured stdout call -----------------------------
2025-09-30 00:00:13 - UserDatabase - INFO - Database initialized at /var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmpgzzs1uox/test.db
2025-09-30 00:00:13 - UserDatabase - INFO - Database initialized at /var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmpgzzs1uox/test.db
2025-09-30 00:00:13 - UserDatabase - INFO - Database initialized at /var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmpgzzs1uox/test.db
------------------------------ Captured log call -------------------------------
INFO     UserDatabase:ticket_master_consolidated.py:2200 Database initialized at /var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmpgzzs1uox/test.db
________________ TestPromptTemplate.test_get_required_variables ________________

self = <tests.test_new_classes.TestPromptTemplate testMethod=test_get_required_variables>

    def test_get_required_variables(self):
        """Test extraction of required variables."""
>       template = PromptTemplate(
            name="test_template",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Generate {num_issues} issues for {repo_name} in {language}",
        )
E       TypeError: PromptTemplate.__init__() got an unexpected keyword argument 'base_template'

tests/test_new_classes.py:165: TypeError
_______________ TestPromptTemplate.test_init_string_prompt_type ________________

self = <tests.test_new_classes.TestPromptTemplate testMethod=test_init_string_prompt_type>

    def test_init_string_prompt_type(self):
        """Test PromptTemplate initialization with string prompt type."""
>       template = PromptTemplate(
            name="test_template",
            prompt_type="issue_generation",
            base_template="Test template",
        )
E       TypeError: PromptTemplate.__init__() got an unexpected keyword argument 'base_template'

tests/test_new_classes.py:129: TypeError
_________________ TestPromptTemplate.test_init_valid_template __________________

self = <tests.test_new_classes.TestPromptTemplate testMethod=test_init_valid_template>

    def test_init_valid_template(self):
        """Test PromptTemplate initialization with valid data."""
>       template = PromptTemplate(
            name="test_template",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Generate {num_issues} issues for {repo_name}",
        )
E       TypeError: PromptTemplate.__init__() got an unexpected keyword argument 'base_template'

tests/test_new_classes.py:114: TypeError
_________________ TestPromptTemplate.test_provider_variations __________________

self = <tests.test_new_classes.TestPromptTemplate testMethod=test_provider_variations>

    def test_provider_variations(self):
        """Test provider-specific template variations."""
>       template = PromptTemplate(
            name="test_template",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Base: {value}",
            provider_variations={
                "ollama": "Ollama: {value}",
                "openai": "OpenAI: {value}",
            },
        )
E       TypeError: PromptTemplate.__init__() got an unexpected keyword argument 'base_template'

tests/test_new_classes.py:178: TypeError
_____________________ TestPromptTemplate.test_render_basic _____________________

self = <tests.test_new_classes.TestPromptTemplate testMethod=test_render_basic>

    def test_render_basic(self):
        """Test basic template rendering."""
>       template = PromptTemplate(
            name="test_template",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Generate {num_issues} issues for {repo_name}",
        )
E       TypeError: PromptTemplate.__init__() got an unexpected keyword argument 'base_template'

tests/test_new_classes.py:139: TypeError
_______________ TestPromptTemplate.test_render_missing_variable ________________

self = <tests.test_new_classes.TestPromptTemplate testMethod=test_render_missing_variable>

    def test_render_missing_variable(self):
        """Test template rendering with missing variable."""
>       template = PromptTemplate(
            name="test_template",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Generate {num_issues} issues for {repo_name}",
        )
E       TypeError: PromptTemplate.__init__() got an unexpected keyword argument 'base_template'

tests/test_new_classes.py:152: TypeError
_________________________ TestPrompt.test_add_template _________________________

self = <tests.test_new_classes.TestPrompt testMethod=test_add_template>

    def setUp(self):
        """Set up test prompt container."""
>       self.prompt = Prompt(default_provider="ollama")
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: Prompt.__init__() got an unexpected keyword argument 'default_provider'

tests/test_new_classes.py:207: TypeError
___________________ TestPrompt.test_create_builtin_templates ___________________

self = <tests.test_new_classes.TestPrompt testMethod=test_create_builtin_templates>

    def setUp(self):
        """Set up test prompt container."""
>       self.prompt = Prompt(default_provider="ollama")
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: Prompt.__init__() got an unexpected keyword argument 'default_provider'

tests/test_new_classes.py:207: TypeError
_________________________ TestPrompt.test_get_template _________________________

self = <tests.test_new_classes.TestPrompt testMethod=test_get_template>

    def setUp(self):
        """Set up test prompt container."""
>       self.prompt = Prompt(default_provider="ollama")
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: Prompt.__init__() got an unexpected keyword argument 'default_provider'

tests/test_new_classes.py:207: TypeError
_____________________________ TestPrompt.test_init _____________________________

self = <tests.test_new_classes.TestPrompt testMethod=test_init>

    def setUp(self):
        """Set up test prompt container."""
>       self.prompt = Prompt(default_provider="ollama")
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: Prompt.__init__() got an unexpected keyword argument 'default_provider'

tests/test_new_classes.py:207: TypeError
________________________ TestPrompt.test_list_templates ________________________

self = <tests.test_new_classes.TestPrompt testMethod=test_list_templates>

    def setUp(self):
        """Set up test prompt container."""
>       self.prompt = Prompt(default_provider="ollama")
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: Prompt.__init__() got an unexpected keyword argument 'default_provider'

tests/test_new_classes.py:207: TypeError
_______________________ TestPrompt.test_render_template ________________________

self = <tests.test_new_classes.TestPrompt testMethod=test_render_template>

    def setUp(self):
        """Set up test prompt container."""
>       self.prompt = Prompt(default_provider="ollama")
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: Prompt.__init__() got an unexpected keyword argument 'default_provider'

tests/test_new_classes.py:207: TypeError
_________________ TestLLMBackend.test_huggingface_backend_init _________________

self = <tests.test_new_classes.TestLLMBackend testMethod=test_huggingface_backend_init>

    def test_huggingface_backend_init(self):
        """Test HuggingFaceBackend initialization."""
        config = {
            "model": "microsoft/DialoGPT-medium",
            "device": "cpu",
            "max_length": 500,
            "temperature": 0.8,
        }
    
        backend = HuggingFaceBackend(config)
    
        self.assertEqual(backend.model_name, "microsoft/DialoGPT-medium")
        self.assertEqual(backend.device, "cpu")
>       self.assertEqual(backend.max_length, 500)
                         ^^^^^^^^^^^^^^^^^^
E       AttributeError: 'HuggingFaceBackend' object has no attribute 'max_length'

tests/test_new_classes.py:334: AttributeError
___________________ TestLLMBackend.test_huggingface_generate ___________________
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1393: in patched
    with self.decoration_helper(patched,
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/contextlib.py:137: in __enter__
    return next(self.gen)
           ^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1375: in decoration_helper
    arg = exit_stack.enter_context(patching)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/contextlib.py:526: in enter_context
    result = _enter(cm)
             ^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1467: in __enter__
    original, local = self.get_original()
                      ^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <unittest.mock._patch object at 0x10ab14230>

    def get_original(self):
        target = self.getter()
        name = self.attribute
    
        original = DEFAULT
        local = False
    
        try:
            original = target.__dict__[name]
        except (AttributeError, KeyError):
            original = getattr(target, name, DEFAULT)
        else:
            local = True
    
        if name in _builtins and isinstance(target, ModuleType):
            self.create = True
    
        if not self.create and original is DEFAULT:
>           raise AttributeError(
                "%s does not have the attribute %r" % (target, name)
            )
E           AttributeError: <class 'ticket_master_consolidated.HuggingFaceBackend'> does not have the attribute '_load_model'

/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1437: AttributeError
________________ TestLLMBackend.test_huggingface_get_model_info ________________

self = <tests.test_new_classes.TestLLMBackend testMethod=test_huggingface_get_model_info>

    def test_huggingface_get_model_info(self):
        """Test HuggingFace model info retrieval."""
        backend = HuggingFaceBackend({"model": "test-model", "device": "cpu"})
    
        info = backend.get_model_info()
        self.assertEqual(info["name"], "test-model")
        self.assertEqual(info["provider"], "huggingface")
>       self.assertEqual(info["device"], "cpu")
                         ^^^^^^^^^^^^^^
E       KeyError: 'device'

tests/test_new_classes.py:376: KeyError
_________________ TestLLMBackend.test_huggingface_is_available _________________
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1393: in patched
    with self.decoration_helper(patched,
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/contextlib.py:137: in __enter__
    return next(self.gen)
           ^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1375: in decoration_helper
    arg = exit_stack.enter_context(patching)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/contextlib.py:526: in enter_context
    result = _enter(cm)
             ^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1467: in __enter__
    original, local = self.get_original()
                      ^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <unittest.mock._patch object at 0x10ab14170>

    def get_original(self):
        target = self.getter()
        name = self.attribute
    
        original = DEFAULT
        local = False
    
        try:
            original = target.__dict__[name]
        except (AttributeError, KeyError):
            original = getattr(target, name, DEFAULT)
        else:
            local = True
    
        if name in _builtins and isinstance(target, ModuleType):
            self.create = True
    
        if not self.create and original is DEFAULT:
>           raise AttributeError(
                "%s does not have the attribute %r" % (target, name)
            )
E           AttributeError: <class 'ticket_master_consolidated.HuggingFaceBackend'> does not have the attribute '_load_model'

/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1437: AttributeError
___________________ TestLLM.test_create_backend_huggingface ____________________

self = <tests.test_new_classes.TestLLM testMethod=test_create_backend_huggingface>

    def test_create_backend_huggingface(self):
        """Test backend creation for HuggingFace provider."""
        config = {"model": "test-model"}
>       llm = LLM(
            LLMProvider.MOCK, {"model": "mock"}
        )  # Use mock for initialization

tests/test_new_classes.py:427: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <ticket_master_consolidated.LLM object at 0x10ae309e0>
provider = <LLMProvider.MOCK: 'mock'>, config = {'model': 'mock'}

    def __init__(self, provider: str, config: Dict[str, Any]) -> None:
        """Initialize LLM with specified provider and configuration."""
        self.provider = provider
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
        # Create appropriate backend
        if provider == "ollama":
            self.backend = OllamaBackend(config)
        else:
>           raise LLMError(f"Unsupported LLM provider: {provider}")
E           ticket_master_consolidated.LLMError: Unsupported LLM provider: LLMProvider.MOCK

src/ticket_master_consolidated.py:1781: LLMError
____________________ TestLLM.test_init_huggingface_provider ____________________

self = <tests.test_new_classes.TestLLM testMethod=test_init_huggingface_provider>

    def test_init_huggingface_provider(self):
        """Test LLM initialization with HuggingFace provider."""
        config = {"model": "microsoft/DialoGPT-medium", "device": "cpu"}
>       llm = LLM("huggingface", config)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_new_classes.py:418: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <ticket_master_consolidated.LLM object at 0x10ab152b0>
provider = 'huggingface'
config = {'device': 'cpu', 'model': 'microsoft/DialoGPT-medium'}

    def __init__(self, provider: str, config: Dict[str, Any]) -> None:
        """Initialize LLM with specified provider and configuration."""
        self.provider = provider
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
        # Create appropriate backend
        if provider == "ollama":
            self.backend = OllamaBackend(config)
        else:
>           raise LLMError(f"Unsupported LLM provider: {provider}")
E           ticket_master_consolidated.LLMError: Unsupported LLM provider: huggingface

src/ticket_master_consolidated.py:1781: LLMError
_____________________ TestLLM.test_init_with_enum_provider _____________________

self = <tests.test_new_classes.TestLLM testMethod=test_init_with_enum_provider>

    def test_init_with_enum_provider(self):
        """Test LLM initialization with enum provider."""
        config = {"host": "localhost", "model": "test"}
>       llm = LLM(LLMProvider.OLLAMA, config)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_new_classes.py:394: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <ticket_master_consolidated.LLM object at 0x10ae32540>
provider = <LLMProvider.OLLAMA: 'ollama'>
config = {'host': 'localhost', 'model': 'test'}

    def __init__(self, provider: str, config: Dict[str, Any]) -> None:
        """Initialize LLM with specified provider and configuration."""
        self.provider = provider
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
        # Create appropriate backend
        if provider == "ollama":
            self.backend = OllamaBackend(config)
        else:
>           raise LLMError(f"Unsupported LLM provider: {provider}")
E           ticket_master_consolidated.LLMError: Unsupported LLM provider: LLMProvider.OLLAMA

src/ticket_master_consolidated.py:1781: LLMError
____________________ TestLLM.test_init_with_string_provider ____________________

self = <tests.test_new_classes.TestLLM testMethod=test_init_with_string_provider>

    def test_init_with_string_provider(self):
        """Test LLM initialization with string provider."""
        config = {"host": "localhost", "model": "test"}
        llm = LLM("ollama", config)
    
>       self.assertEqual(llm.provider, LLMProvider.OLLAMA)
E       AssertionError: 'ollama' != <LLMProvider.OLLAMA: 'ollama'>

tests/test_new_classes.py:388: AssertionError
____________________________ TestLLM.test_metadata _____________________________

self = <tests.test_new_classes.TestLLM testMethod=test_metadata>

    def test_metadata(self):
        """Test LLM metadata."""
        config = {"model": "test_model"}
>       llm = LLM(LLMProvider.OLLAMA, config)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_new_classes.py:408: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <ticket_master_consolidated.LLM object at 0x10a9cdd30>
provider = <LLMProvider.OLLAMA: 'ollama'>, config = {'model': 'test_model'}

    def __init__(self, provider: str, config: Dict[str, Any]) -> None:
        """Initialize LLM with specified provider and configuration."""
        self.provider = provider
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
        # Create appropriate backend
        if provider == "ollama":
            self.backend = OllamaBackend(config)
        else:
>           raise LLMError(f"Unsupported LLM provider: {provider}")
E           ticket_master_consolidated.LLMError: Unsupported LLM provider: LLMProvider.OLLAMA

src/ticket_master_consolidated.py:1781: LLMError
_____________________ TestPipelineStep.test_execute_basic ______________________

self = <tests.test_new_classes.TestPipelineStep testMethod=test_execute_basic>

    def test_execute_basic(self):
        """Test basic step execution."""
>       template = PromptTemplate(
            "test", PromptType.ISSUE_GENERATION, "Generate {count} issues"
        )
E       TypeError: PromptTemplate.__init__() missing 1 required positional argument: 'variables'

tests/test_new_classes.py:461: TypeError
__________________________ TestPipelineStep.test_init __________________________

self = <tests.test_new_classes.TestPipelineStep testMethod=test_init>

    def test_init(self):
        """Test PipelineStep initialization."""
>       template = PromptTemplate(
            "test", PromptType.ISSUE_GENERATION, "Test {value}"
        )
E       TypeError: PromptTemplate.__init__() missing 1 required positional argument: 'variables'

tests/test_new_classes.py:451: TypeError
____________________________ TestPipe.test_add_step ____________________________

self = <tests.test_new_classes.TestPipe testMethod=test_add_step>

    def test_add_step(self):
        """Test adding steps to pipeline."""
>       pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: Pipe.__init__() takes 1 positional argument but 4 were given

tests/test_new_classes.py:502: TypeError
______________________________ TestPipe.test_init ______________________________

self = <tests.test_new_classes.TestPipe testMethod=test_init>

    def test_init(self):
        """Test Pipe initialization."""
>       pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: Pipe.__init__() takes 1 positional argument but 4 were given

tests/test_new_classes.py:495: TypeError
_______________________ TestPipe.test_validate_pipeline ________________________

self = <tests.test_new_classes.TestPipe testMethod=test_validate_pipeline>

    def test_validate_pipeline(self):
        """Test pipeline validation."""
>       pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: Pipe.__init__() takes 1 positional argument but 4 were given

tests/test_new_classes.py:513: TypeError
_________________ TestDataScraper.test_scrape_content_analysis _________________

self = <tests.test_new_classes.TestDataScraper testMethod=test_scrape_content_analysis>

    def test_scrape_content_analysis(self):
        """Test content analysis."""
>       analysis = self.scraper.scrape_content_analysis()
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: 'DataScraper' object has no attribute 'scrape_content_analysis'

tests/test_new_classes.py:558: AttributeError
----------------------------- Captured stdout call -----------------------------
2025-09-30 00:00:13 - Repository - INFO - Initialized repository at /Users/dhodgson/Desktop/Ticket-Master
2025-09-30 00:00:13 - Repository - INFO - Initialized repository at /Users/dhodgson/Desktop/Ticket-Master
2025-09-30 00:00:13 - Repository - INFO - Initialized repository at /Users/dhodgson/Desktop/Ticket-Master
------------------------------ Captured log call -------------------------------
INFO     Repository:ticket_master_consolidated.py:879 Initialized repository at /Users/dhodgson/Desktop/Ticket-Master
__________________ TestDataScraper.test_scrape_file_structure __________________

self = <tests.test_new_classes.TestDataScraper testMethod=test_scrape_file_structure>

    def test_scrape_file_structure(self):
        """Test file structure analysis."""
>       structure = self.scraper.scrape_file_structure()
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: 'DataScraper' object has no attribute 'scrape_file_structure'

tests/test_new_classes.py:549: AttributeError
----------------------------- Captured stdout call -----------------------------
2025-09-30 00:00:13 - Repository - INFO - Initialized repository at /Users/dhodgson/Desktop/Ticket-Master
2025-09-30 00:00:13 - Repository - INFO - Initialized repository at /Users/dhodgson/Desktop/Ticket-Master
2025-09-30 00:00:13 - Repository - INFO - Initialized repository at /Users/dhodgson/Desktop/Ticket-Master
------------------------------ Captured log call -------------------------------
INFO     Repository:ticket_master_consolidated.py:879 Initialized repository at /Users/dhodgson/Desktop/Ticket-Master
_________________ TestDataScraper.test_scrape_repository_info __________________

self = <tests.test_new_classes.TestDataScraper testMethod=test_scrape_repository_info>

    def test_scrape_repository_info(self):
        """Test repository information scraping."""
>       info = self.scraper.scrape_repository_info()
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: 'DataScraper' object has no attribute 'scrape_repository_info'

tests/test_new_classes.py:541: AttributeError
----------------------------- Captured stdout call -----------------------------
2025-09-30 00:00:13 - Repository - INFO - Initialized repository at /Users/dhodgson/Desktop/Ticket-Master
2025-09-30 00:00:13 - Repository - INFO - Initialized repository at /Users/dhodgson/Desktop/Ticket-Master
2025-09-30 00:00:13 - Repository - INFO - Initialized repository at /Users/dhodgson/Desktop/Ticket-Master
------------------------------ Captured log call -------------------------------
INFO     Repository:ticket_master_consolidated.py:879 Initialized repository at /Users/dhodgson/Desktop/Ticket-Master
_____________ TestOllamaPromptProcessor.test_batch_process_prompts _____________

self = <tests.test_ollama_tools.TestOllamaPromptProcessor testMethod=test_batch_process_prompts>

    def setUp(self):
        """Set up test fixtures."""
>       with patch("ollama_tools.ollama"):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_ollama_tools.py:26: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1451: in __enter__
    self.target = self.getter()
                  ^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pkgutil.py:513: in resolve_name
    mod = importlib.import_module(modname)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:1387: in _gcd_import
    ???
<frozen importlib._bootstrap>:1360: in _find_and_load
    ???
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

name = 'ollama_tools', import_ = <function _gcd_import at 0x1022ec0e0>

>   ???
E   ModuleNotFoundError: No module named 'ollama_tools'

<frozen importlib._bootstrap>:1324: ModuleNotFoundError
___________ TestOllamaPromptProcessor.test_check_model_availability ____________

self = <tests.test_ollama_tools.TestOllamaPromptProcessor testMethod=test_check_model_availability>

    def setUp(self):
        """Set up test fixtures."""
>       with patch("ollama_tools.ollama"):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_ollama_tools.py:26: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1451: in __enter__
    self.target = self.getter()
                  ^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pkgutil.py:513: in resolve_name
    mod = importlib.import_module(modname)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:1387: in _gcd_import
    ???
<frozen importlib._bootstrap>:1360: in _find_and_load
    ???
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

name = 'ollama_tools', import_ = <function _gcd_import at 0x1022ec0e0>

>   ???
E   ModuleNotFoundError: No module named 'ollama_tools'

<frozen importlib._bootstrap>:1324: ModuleNotFoundError
_________ TestOllamaPromptProcessor.test_generate_issues_from_analysis _________

self = <tests.test_ollama_tools.TestOllamaPromptProcessor testMethod=test_generate_issues_from_analysis>

    def setUp(self):
        """Set up test fixtures."""
>       with patch("ollama_tools.ollama"):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_ollama_tools.py:26: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1451: in __enter__
    self.target = self.getter()
                  ^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pkgutil.py:513: in resolve_name
    mod = importlib.import_module(modname)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:1387: in _gcd_import
    ???
<frozen importlib._bootstrap>:1360: in _find_and_load
    ???
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

name = 'ollama_tools', import_ = <function _gcd_import at 0x1022ec0e0>

>   ???
E   ModuleNotFoundError: No module named 'ollama_tools'

<frozen importlib._bootstrap>:1324: ModuleNotFoundError
________________ TestOllamaPromptProcessor.test_get_model_info _________________

self = <tests.test_ollama_tools.TestOllamaPromptProcessor testMethod=test_get_model_info>

    def setUp(self):
        """Set up test fixtures."""
>       with patch("ollama_tools.ollama"):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_ollama_tools.py:26: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1451: in __enter__
    self.target = self.getter()
                  ^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pkgutil.py:513: in resolve_name
    mod = importlib.import_module(modname)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:1387: in _gcd_import
    ???
<frozen importlib._bootstrap>:1360: in _find_and_load
    ???
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

name = 'ollama_tools', import_ = <function _gcd_import at 0x1022ec0e0>

>   ???
E   ModuleNotFoundError: No module named 'ollama_tools'

<frozen importlib._bootstrap>:1324: ModuleNotFoundError
_____________________ TestOllamaPromptProcessor.test_init ______________________

self = <tests.test_ollama_tools.TestOllamaPromptProcessor testMethod=test_init>

    def setUp(self):
        """Set up test fixtures."""
>       with patch("ollama_tools.ollama"):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_ollama_tools.py:26: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1451: in __enter__
    self.target = self.getter()
                  ^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pkgutil.py:513: in resolve_name
    mod = importlib.import_module(modname)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:1387: in _gcd_import
    ???
<frozen importlib._bootstrap>:1360: in _find_and_load
    ???
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

name = 'ollama_tools', import_ = <function _gcd_import at 0x1022ec0e0>

>   ???
E   ModuleNotFoundError: No module named 'ollama_tools'

<frozen importlib._bootstrap>:1324: ModuleNotFoundError
_________________ TestOllamaPromptProcessor.test_install_model _________________

self = <tests.test_ollama_tools.TestOllamaPromptProcessor testMethod=test_install_model>

    def setUp(self):
        """Set up test fixtures."""
>       with patch("ollama_tools.ollama"):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_ollama_tools.py:26: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1451: in __enter__
    self.target = self.getter()
                  ^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pkgutil.py:513: in resolve_name
    mod = importlib.import_module(modname)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:1387: in _gcd_import
    ???
<frozen importlib._bootstrap>:1360: in _find_and_load
    ???
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

name = 'ollama_tools', import_ = <function _gcd_import at 0x1022ec0e0>

>   ???
E   ModuleNotFoundError: No module named 'ollama_tools'

<frozen importlib._bootstrap>:1324: ModuleNotFoundError
__________ TestOllamaPromptProcessor.test_parse_issues_response_json ___________

self = <tests.test_ollama_tools.TestOllamaPromptProcessor testMethod=test_parse_issues_response_json>

    def setUp(self):
        """Set up test fixtures."""
>       with patch("ollama_tools.ollama"):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_ollama_tools.py:26: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1451: in __enter__
    self.target = self.getter()
                  ^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pkgutil.py:513: in resolve_name
    mod = importlib.import_module(modname)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:1387: in _gcd_import
    ???
<frozen importlib._bootstrap>:1360: in _find_and_load
    ???
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

name = 'ollama_tools', import_ = <function _gcd_import at 0x1022ec0e0>

>   ???
E   ModuleNotFoundError: No module named 'ollama_tools'

<frozen importlib._bootstrap>:1324: ModuleNotFoundError
__________ TestOllamaPromptProcessor.test_parse_issues_response_text ___________

self = <tests.test_ollama_tools.TestOllamaPromptProcessor testMethod=test_parse_issues_response_text>

    def setUp(self):
        """Set up test fixtures."""
>       with patch("ollama_tools.ollama"):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_ollama_tools.py:26: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1451: in __enter__
    self.target = self.getter()
                  ^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pkgutil.py:513: in resolve_name
    mod = importlib.import_module(modname)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:1387: in _gcd_import
    ???
<frozen importlib._bootstrap>:1360: in _find_and_load
    ???
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

name = 'ollama_tools', import_ = <function _gcd_import at 0x1022ec0e0>

>   ???
E   ModuleNotFoundError: No module named 'ollama_tools'

<frozen importlib._bootstrap>:1324: ModuleNotFoundError
___________ TestOllamaPromptProcessor.test_process_prompt_api_error ____________

self = <tests.test_ollama_tools.TestOllamaPromptProcessor testMethod=test_process_prompt_api_error>

    def setUp(self):
        """Set up test fixtures."""
>       with patch("ollama_tools.ollama"):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_ollama_tools.py:26: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1451: in __enter__
    self.target = self.getter()
                  ^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pkgutil.py:513: in resolve_name
    mod = importlib.import_module(modname)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:1387: in _gcd_import
    ???
<frozen importlib._bootstrap>:1360: in _find_and_load
    ???
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

name = 'ollama_tools', import_ = <function _gcd_import at 0x1022ec0e0>

>   ???
E   ModuleNotFoundError: No module named 'ollama_tools'

<frozen importlib._bootstrap>:1324: ModuleNotFoundError
____________ TestOllamaPromptProcessor.test_process_prompt_success _____________

self = <tests.test_ollama_tools.TestOllamaPromptProcessor testMethod=test_process_prompt_success>

    def setUp(self):
        """Set up test fixtures."""
>       with patch("ollama_tools.ollama"):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_ollama_tools.py:26: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1451: in __enter__
    self.target = self.getter()
                  ^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pkgutil.py:513: in resolve_name
    mod = importlib.import_module(modname)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:1387: in _gcd_import
    ???
<frozen importlib._bootstrap>:1360: in _find_and_load
    ???
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

name = 'ollama_tools', import_ = <function _gcd_import at 0x1022ec0e0>

>   ???
E   ModuleNotFoundError: No module named 'ollama_tools'

<frozen importlib._bootstrap>:1324: ModuleNotFoundError
__________ TestOllamaPromptProcessor.test_process_prompt_with_options __________

self = <tests.test_ollama_tools.TestOllamaPromptProcessor testMethod=test_process_prompt_with_options>

    def setUp(self):
        """Set up test fixtures."""
>       with patch("ollama_tools.ollama"):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_ollama_tools.py:26: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1451: in __enter__
    self.target = self.getter()
                  ^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pkgutil.py:513: in resolve_name
    mod = importlib.import_module(modname)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:1387: in _gcd_import
    ???
<frozen importlib._bootstrap>:1360: in _find_and_load
    ???
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

name = 'ollama_tools', import_ = <function _gcd_import at 0x1022ec0e0>

>   ???
E   ModuleNotFoundError: No module named 'ollama_tools'

<frozen importlib._bootstrap>:1324: ModuleNotFoundError
_ TestOllamaPromptValidator.test_validate_prompt_template_missing_ollama_variation _

self = <tests.test_ollama_tools.TestOllamaPromptValidator testMethod=test_validate_prompt_template_missing_ollama_variation>

    def test_validate_prompt_template_missing_ollama_variation(self):
        """Test validation warns about missing Ollama variation."""
>       template = PromptTemplate(
            name="test_template",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Generate {num_issues} issues for {repo_path}",
            provider_variations={"openai": "Create issues using OpenAI"},
        )
E       TypeError: PromptTemplate.__init__() got an unexpected keyword argument 'base_template'

tests/test_ollama_tools.py:367: TypeError
_ TestOllamaPromptValidator.test_validate_prompt_template_missing_required_vars _

self = <tests.test_ollama_tools.TestOllamaPromptValidator testMethod=test_validate_prompt_template_missing_required_vars>

    def test_validate_prompt_template_missing_required_vars(self):
        """Test validation identifies missing required variables."""
>       template = PromptTemplate(
            name="test_template",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Generate some issues",  # Missing {num_issues} and {repo_path}
            provider_variations={"ollama": "Create issues"},
        )
E       TypeError: PromptTemplate.__init__() got an unexpected keyword argument 'base_template'

tests/test_ollama_tools.py:382: TypeError
_______ TestOllamaPromptValidator.test_validate_prompt_template_too_long _______

self = <tests.test_ollama_tools.TestOllamaPromptValidator testMethod=test_validate_prompt_template_too_long>

    def test_validate_prompt_template_too_long(self):
        """Test validation warns about very long templates."""
        long_template = "A" * 5000  # Very long template
    
>       template = PromptTemplate(
            name="test_template",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template=long_template,
            provider_variations={"ollama": long_template},
        )
E       TypeError: PromptTemplate.__init__() got an unexpected keyword argument 'base_template'

tests/test_ollama_tools.py:399: TypeError
________ TestOllamaPromptValidator.test_validate_prompt_template_valid _________

self = <tests.test_ollama_tools.TestOllamaPromptValidator testMethod=test_validate_prompt_template_valid>

    def test_validate_prompt_template_valid(self):
        """Test validation of a valid prompt template."""
>       template = PromptTemplate(
            name="test_template",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Generate {num_issues} issues for {repo_path}",
            provider_variations={
                "ollama": "Create {num_issues} GitHub issues for {repo_path}"
            },
        )
E       TypeError: PromptTemplate.__init__() got an unexpected keyword argument 'base_template'

tests/test_ollama_tools.py:349: TypeError
__________ TestOllamaPromptValidator.test_validate_variables_missing ___________

self = <tests.test_ollama_tools.TestOllamaPromptValidator testMethod=test_validate_variables_missing>

    def test_validate_variables_missing(self):
        """Test validation identifies missing variables."""
>       template = PromptTemplate(
            name="test",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Generate {num} issues for {repo} in {branch}",
        )
E       TypeError: PromptTemplate.__init__() got an unexpected keyword argument 'base_template'

tests/test_ollama_tools.py:435: TypeError
________ TestOllamaPromptValidator.test_validate_variables_none_values _________

self = <tests.test_ollama_tools.TestOllamaPromptValidator testMethod=test_validate_variables_none_values>

    def test_validate_variables_none_values(self):
        """Test validation warns about None values."""
>       template = PromptTemplate(
            name="test",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Generate {num} issues for {repo}",
        )
E       TypeError: PromptTemplate.__init__() got an unexpected keyword argument 'base_template'

tests/test_ollama_tools.py:473: TypeError
___________ TestOllamaPromptValidator.test_validate_variables_unused ___________

self = <tests.test_ollama_tools.TestOllamaPromptValidator testMethod=test_validate_variables_unused>

    def test_validate_variables_unused(self):
        """Test validation warns about unused variables."""
>       template = PromptTemplate(
            name="test",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Generate {num} issues",
        )
E       TypeError: PromptTemplate.__init__() got an unexpected keyword argument 'base_template'

tests/test_ollama_tools.py:453: TypeError
___________ TestOllamaPromptValidator.test_validate_variables_valid ____________

self = <tests.test_ollama_tools.TestOllamaPromptValidator testMethod=test_validate_variables_valid>

    def test_validate_variables_valid(self):
        """Test validation of valid variables."""
>       template = PromptTemplate(
            name="test",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Generate {num} issues for {repo}",
        )
E       TypeError: PromptTemplate.__init__() got an unexpected keyword argument 'base_template'

tests/test_ollama_tools.py:418: TypeError
________ TestOllamaAdvancedIntegration.test_concurrent_request_handling ________

self = <tests.test_ollama_tools.TestOllamaAdvancedIntegration testMethod=test_concurrent_request_handling>

    def setUp(self):
        """Set up test fixtures."""
>       with patch("ollama_tools.ollama"):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_ollama_tools.py:518: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1451: in __enter__
    self.target = self.getter()
                  ^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pkgutil.py:513: in resolve_name
    mod = importlib.import_module(modname)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:1387: in _gcd_import
    ???
<frozen importlib._bootstrap>:1360: in _find_and_load
    ???
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

name = 'ollama_tools', import_ = <function _gcd_import at 0x1022ec0e0>

>   ???
E   ModuleNotFoundError: No module named 'ollama_tools'

<frozen importlib._bootstrap>:1324: ModuleNotFoundError
__________ TestOllamaAdvancedIntegration.test_connection_retry_logic ___________

self = <tests.test_ollama_tools.TestOllamaAdvancedIntegration testMethod=test_connection_retry_logic>

    def setUp(self):
        """Set up test fixtures."""
>       with patch("ollama_tools.ollama"):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_ollama_tools.py:518: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1451: in __enter__
    self.target = self.getter()
                  ^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pkgutil.py:513: in resolve_name
    mod = importlib.import_module(modname)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:1387: in _gcd_import
    ???
<frozen importlib._bootstrap>:1360: in _find_and_load
    ???
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

name = 'ollama_tools', import_ = <function _gcd_import at 0x1022ec0e0>

>   ???
E   ModuleNotFoundError: No module named 'ollama_tools'

<frozen importlib._bootstrap>:1324: ModuleNotFoundError
_______ TestOllamaAdvancedIntegration.test_custom_generation_parameters ________

self = <tests.test_ollama_tools.TestOllamaAdvancedIntegration testMethod=test_custom_generation_parameters>

    def setUp(self):
        """Set up test fixtures."""
>       with patch("ollama_tools.ollama"):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_ollama_tools.py:518: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1451: in __enter__
    self.target = self.getter()
                  ^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pkgutil.py:513: in resolve_name
    mod = importlib.import_module(modname)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:1387: in _gcd_import
    ???
<frozen importlib._bootstrap>:1360: in _find_and_load
    ???
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

name = 'ollama_tools', import_ = <function _gcd_import at 0x1022ec0e0>

>   ???
E   ModuleNotFoundError: No module named 'ollama_tools'

<frozen importlib._bootstrap>:1324: ModuleNotFoundError
_____ TestOllamaAdvancedIntegration.test_memory_optimization_large_prompts _____

self = <tests.test_ollama_tools.TestOllamaAdvancedIntegration testMethod=test_memory_optimization_large_prompts>

    def setUp(self):
        """Set up test fixtures."""
>       with patch("ollama_tools.ollama"):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_ollama_tools.py:518: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1451: in __enter__
    self.target = self.getter()
                  ^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pkgutil.py:513: in resolve_name
    mod = importlib.import_module(modname)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:1387: in _gcd_import
    ???
<frozen importlib._bootstrap>:1360: in _find_and_load
    ???
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

name = 'ollama_tools', import_ = <function _gcd_import at 0x1022ec0e0>

>   ???
E   ModuleNotFoundError: No module named 'ollama_tools'

<frozen importlib._bootstrap>:1324: ModuleNotFoundError
____________ TestOllamaAdvancedIntegration.test_model_info_detailed ____________

self = <tests.test_ollama_tools.TestOllamaAdvancedIntegration testMethod=test_model_info_detailed>

    def setUp(self):
        """Set up test fixtures."""
>       with patch("ollama_tools.ollama"):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_ollama_tools.py:518: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1451: in __enter__
    self.target = self.getter()
                  ^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pkgutil.py:513: in resolve_name
    mod = importlib.import_module(modname)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:1387: in _gcd_import
    ???
<frozen importlib._bootstrap>:1360: in _find_and_load
    ???
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

name = 'ollama_tools', import_ = <function _gcd_import at 0x1022ec0e0>

>   ???
E   ModuleNotFoundError: No module named 'ollama_tools'

<frozen importlib._bootstrap>:1324: ModuleNotFoundError
___ TestOllamaAdvancedIntegration.test_model_installation_failure_scenarios ____

self = <tests.test_ollama_tools.TestOllamaAdvancedIntegration testMethod=test_model_installation_failure_scenarios>

    def setUp(self):
        """Set up test fixtures."""
>       with patch("ollama_tools.ollama"):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_ollama_tools.py:518: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1451: in __enter__
    self.target = self.getter()
                  ^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pkgutil.py:513: in resolve_name
    mod = importlib.import_module(modname)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:1387: in _gcd_import
    ???
<frozen importlib._bootstrap>:1360: in _find_and_load
    ???
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

name = 'ollama_tools', import_ = <function _gcd_import at 0x1022ec0e0>

>   ???
E   ModuleNotFoundError: No module named 'ollama_tools'

<frozen importlib._bootstrap>:1324: ModuleNotFoundError
_____ TestOllamaAdvancedIntegration.test_model_installation_with_progress ______

self = <tests.test_ollama_tools.TestOllamaAdvancedIntegration testMethod=test_model_installation_with_progress>

    def setUp(self):
        """Set up test fixtures."""
>       with patch("ollama_tools.ollama"):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_ollama_tools.py:518: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1451: in __enter__
    self.target = self.getter()
                  ^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pkgutil.py:513: in resolve_name
    mod = importlib.import_module(modname)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:1387: in _gcd_import
    ???
<frozen importlib._bootstrap>:1360: in _find_and_load
    ???
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

name = 'ollama_tools', import_ = <function _gcd_import at 0x1022ec0e0>

>   ???
E   ModuleNotFoundError: No module named 'ollama_tools'

<frozen importlib._bootstrap>:1324: ModuleNotFoundError
______________ TestOllamaAdvancedIntegration.test_model_switching ______________

self = <tests.test_ollama_tools.TestOllamaAdvancedIntegration testMethod=test_model_switching>

    def setUp(self):
        """Set up test fixtures."""
>       with patch("ollama_tools.ollama"):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_ollama_tools.py:518: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1451: in __enter__
    self.target = self.getter()
                  ^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pkgutil.py:513: in resolve_name
    mod = importlib.import_module(modname)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:1387: in _gcd_import
    ???
<frozen importlib._bootstrap>:1360: in _find_and_load
    ???
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

name = 'ollama_tools', import_ = <function _gcd_import at 0x1022ec0e0>

>   ???
E   ModuleNotFoundError: No module named 'ollama_tools'

<frozen importlib._bootstrap>:1324: ModuleNotFoundError
________ TestOllamaAdvancedIntegration.test_response_streaming_handling ________

self = <tests.test_ollama_tools.TestOllamaAdvancedIntegration testMethod=test_response_streaming_handling>

    def setUp(self):
        """Set up test fixtures."""
>       with patch("ollama_tools.ollama"):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_ollama_tools.py:518: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1451: in __enter__
    self.target = self.getter()
                  ^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pkgutil.py:513: in resolve_name
    mod = importlib.import_module(modname)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:1387: in _gcd_import
    ???
<frozen importlib._bootstrap>:1360: in _find_and_load
    ???
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

name = 'ollama_tools', import_ = <function _gcd_import at 0x1022ec0e0>

>   ???
E   ModuleNotFoundError: No module named 'ollama_tools'

<frozen importlib._bootstrap>:1324: ModuleNotFoundError
__________ TestOllamaErrorRecovery.test_insufficient_memory_handling ___________

self = <tests.test_ollama_tools.TestOllamaErrorRecovery testMethod=test_insufficient_memory_handling>
mock_ollama = <MagicMock name='ollama' id='4478968288'>

    @patch("ticket_master_consolidated.ollama")
    def test_insufficient_memory_handling(self, mock_ollama):
        """Test handling when system has insufficient memory for model."""
        mock_client = Mock()
        mock_ollama.Client.return_value = mock_client
        mock_client.generate.side_effect = Exception("Out of memory")
    
>       processor = OllamaPromptProcessor(model="very-large-model")
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: OllamaPromptProcessor.__init__() got an unexpected keyword argument 'model'

tests/test_ollama_tools.py:814: TypeError
_____________ TestOllamaErrorRecovery.test_invalid_prompt_handling _____________

self = <tests.test_ollama_tools.TestOllamaErrorRecovery testMethod=test_invalid_prompt_handling>
mock_ollama = <MagicMock name='ollama' id='4473320176'>

    @patch("ticket_master_consolidated.ollama")
    def test_invalid_prompt_handling(self, mock_ollama):
        """Test handling of invalid or malformed prompts."""
        mock_client = Mock()
        mock_ollama.Client.return_value = mock_client
        mock_client.generate.return_value = {
            "response": "Invalid prompt handled"
        }
    
>       processor = OllamaPromptProcessor(model="test-model")
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: OllamaPromptProcessor.__init__() got an unexpected keyword argument 'model'

tests/test_ollama_tools.py:834: TypeError
_________ TestOllamaErrorRecovery.test_model_loading_timeout_handling __________

self = <tests.test_ollama_tools.TestOllamaErrorRecovery testMethod=test_model_loading_timeout_handling>
mock_ollama = <MagicMock name='ollama' id='4478309376'>

    @patch("ticket_master_consolidated.ollama")
    def test_model_loading_timeout_handling(self, mock_ollama):
        """Test handling of model loading timeouts."""
        mock_client = Mock()
        mock_ollama.Client.return_value = mock_client
    
        # Simulate timeout during model loading
        import socket
    
        mock_client.generate.side_effect = socket.timeout(
            "Model loading timeout"
        )
    
>       processor = OllamaPromptProcessor(model="large-model")
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: OllamaPromptProcessor.__init__() got an unexpected keyword argument 'model'

tests/test_ollama_tools.py:797: TypeError
_____ TestLargeRepositoryPerformance.test_bulk_data_processing_performance _____
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1393: in patched
    with self.decoration_helper(patched,
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/contextlib.py:137: in __enter__
    return next(self.gen)
           ^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1375: in decoration_helper
    arg = exit_stack.enter_context(patching)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/contextlib.py:526: in enter_context
    result = _enter(cm)
             ^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1451: in __enter__
    self.target = self.getter()
                  ^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

name = 'src.ticket_master.data_scraper'

    def resolve_name(name):
        """
        Resolve a name to an object.
    
        It is expected that `name` will be a string in one of the following
        formats, where W is shorthand for a valid Python identifier and dot stands
        for a literal period in these pseudo-regexes:
    
        W(.W)*
        W(.W)*:(W(.W)*)?
    
        The first form is intended for backward compatibility only. It assumes that
        some part of the dotted name is a package, and the rest is an object
        somewhere within that package, possibly nested inside other objects.
        Because the place where the package stops and the object hierarchy starts
        can't be inferred by inspection, repeated attempts to import must be done
        with this form.
    
        In the second form, the caller makes the division point clear through the
        provision of a single colon: the dotted name to the left of the colon is a
        package to be imported, and the dotted name to the right is the object
        hierarchy within that package. Only one import is needed in this form. If
        it ends with the colon, then a module object is returned.
    
        The function will return an object (which might be a module), or raise one
        of the following exceptions:
    
        ValueError - if `name` isn't in a recognised format
        ImportError - if an import failed when it shouldn't have
        AttributeError - if a failure occurred when traversing the object hierarchy
                         within the imported package to get to the desired object.
        """
        global _NAME_PATTERN
        if _NAME_PATTERN is None:
            # Lazy import to speedup Python startup time
            import re
            dotted_words = r'(?!\d)(\w+)(\.(?!\d)(\w+))*'
            _NAME_PATTERN = re.compile(f'^(?P<pkg>{dotted_words})'
                                       f'(?P<cln>:(?P<obj>{dotted_words})?)?$',
                                       re.UNICODE)
    
        m = _NAME_PATTERN.match(name)
        if not m:
            raise ValueError(f'invalid format: {name!r}')
        gd = m.groupdict()
        if gd.get('cln'):
            # there is a colon - a one-step import is all that's needed
            mod = importlib.import_module(gd['pkg'])
            parts = gd.get('obj')
            parts = parts.split('.') if parts else []
        else:
            # no colon - have to iterate to find the package boundary
            parts = name.split('.')
            modname = parts.pop(0)
            # first part *must* be a module/package.
            mod = importlib.import_module(modname)
            while parts:
                p = parts[0]
                s = f'{modname}.{p}'
                try:
                    mod = importlib.import_module(s)
                    parts.pop(0)
                    modname = s
                except ImportError:
                    break
        # if we reach this point, mod is the module, already imported, and
        # parts is the list of parts in the object hierarchy to be traversed, or
        # an empty list if just the module is wanted.
        result = mod
        for p in parts:
>           result = getattr(result, p)
                     ^^^^^^^^^^^^^^^^^^
E           AttributeError: module 'src' has no attribute 'ticket_master'

/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pkgutil.py:528: AttributeError
_____ TestLargeRepositoryPerformance.test_large_commit_history_performance _____
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1393: in patched
    with self.decoration_helper(patched,
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/contextlib.py:137: in __enter__
    return next(self.gen)
           ^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1375: in decoration_helper
    arg = exit_stack.enter_context(patching)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/contextlib.py:526: in enter_context
    result = _enter(cm)
             ^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1451: in __enter__
    self.target = self.getter()
                  ^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

name = 'src.ticket_master.repository.git'

    def resolve_name(name):
        """
        Resolve a name to an object.
    
        It is expected that `name` will be a string in one of the following
        formats, where W is shorthand for a valid Python identifier and dot stands
        for a literal period in these pseudo-regexes:
    
        W(.W)*
        W(.W)*:(W(.W)*)?
    
        The first form is intended for backward compatibility only. It assumes that
        some part of the dotted name is a package, and the rest is an object
        somewhere within that package, possibly nested inside other objects.
        Because the place where the package stops and the object hierarchy starts
        can't be inferred by inspection, repeated attempts to import must be done
        with this form.
    
        In the second form, the caller makes the division point clear through the
        provision of a single colon: the dotted name to the left of the colon is a
        package to be imported, and the dotted name to the right is the object
        hierarchy within that package. Only one import is needed in this form. If
        it ends with the colon, then a module object is returned.
    
        The function will return an object (which might be a module), or raise one
        of the following exceptions:
    
        ValueError - if `name` isn't in a recognised format
        ImportError - if an import failed when it shouldn't have
        AttributeError - if a failure occurred when traversing the object hierarchy
                         within the imported package to get to the desired object.
        """
        global _NAME_PATTERN
        if _NAME_PATTERN is None:
            # Lazy import to speedup Python startup time
            import re
            dotted_words = r'(?!\d)(\w+)(\.(?!\d)(\w+))*'
            _NAME_PATTERN = re.compile(f'^(?P<pkg>{dotted_words})'
                                       f'(?P<cln>:(?P<obj>{dotted_words})?)?$',
                                       re.UNICODE)
    
        m = _NAME_PATTERN.match(name)
        if not m:
            raise ValueError(f'invalid format: {name!r}')
        gd = m.groupdict()
        if gd.get('cln'):
            # there is a colon - a one-step import is all that's needed
            mod = importlib.import_module(gd['pkg'])
            parts = gd.get('obj')
            parts = parts.split('.') if parts else []
        else:
            # no colon - have to iterate to find the package boundary
            parts = name.split('.')
            modname = parts.pop(0)
            # first part *must* be a module/package.
            mod = importlib.import_module(modname)
            while parts:
                p = parts[0]
                s = f'{modname}.{p}'
                try:
                    mod = importlib.import_module(s)
                    parts.pop(0)
                    modname = s
                except ImportError:
                    break
        # if we reach this point, mod is the module, already imported, and
        # parts is the list of parts in the object hierarchy to be traversed, or
        # an empty list if just the module is wanted.
        result = mod
        for p in parts:
>           result = getattr(result, p)
                     ^^^^^^^^^^^^^^^^^^
E           AttributeError: module 'src' has no attribute 'ticket_master'

/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pkgutil.py:528: AttributeError
_______ TestLargeRepositoryPerformance.test_large_file_count_performance _______
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1393: in patched
    with self.decoration_helper(patched,
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/contextlib.py:137: in __enter__
    return next(self.gen)
           ^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1375: in decoration_helper
    arg = exit_stack.enter_context(patching)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/contextlib.py:526: in enter_context
    result = _enter(cm)
             ^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1451: in __enter__
    self.target = self.getter()
                  ^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

name = 'src.ticket_master.repository.git'

    def resolve_name(name):
        """
        Resolve a name to an object.
    
        It is expected that `name` will be a string in one of the following
        formats, where W is shorthand for a valid Python identifier and dot stands
        for a literal period in these pseudo-regexes:
    
        W(.W)*
        W(.W)*:(W(.W)*)?
    
        The first form is intended for backward compatibility only. It assumes that
        some part of the dotted name is a package, and the rest is an object
        somewhere within that package, possibly nested inside other objects.
        Because the place where the package stops and the object hierarchy starts
        can't be inferred by inspection, repeated attempts to import must be done
        with this form.
    
        In the second form, the caller makes the division point clear through the
        provision of a single colon: the dotted name to the left of the colon is a
        package to be imported, and the dotted name to the right is the object
        hierarchy within that package. Only one import is needed in this form. If
        it ends with the colon, then a module object is returned.
    
        The function will return an object (which might be a module), or raise one
        of the following exceptions:
    
        ValueError - if `name` isn't in a recognised format
        ImportError - if an import failed when it shouldn't have
        AttributeError - if a failure occurred when traversing the object hierarchy
                         within the imported package to get to the desired object.
        """
        global _NAME_PATTERN
        if _NAME_PATTERN is None:
            # Lazy import to speedup Python startup time
            import re
            dotted_words = r'(?!\d)(\w+)(\.(?!\d)(\w+))*'
            _NAME_PATTERN = re.compile(f'^(?P<pkg>{dotted_words})'
                                       f'(?P<cln>:(?P<obj>{dotted_words})?)?$',
                                       re.UNICODE)
    
        m = _NAME_PATTERN.match(name)
        if not m:
            raise ValueError(f'invalid format: {name!r}')
        gd = m.groupdict()
        if gd.get('cln'):
            # there is a colon - a one-step import is all that's needed
            mod = importlib.import_module(gd['pkg'])
            parts = gd.get('obj')
            parts = parts.split('.') if parts else []
        else:
            # no colon - have to iterate to find the package boundary
            parts = name.split('.')
            modname = parts.pop(0)
            # first part *must* be a module/package.
            mod = importlib.import_module(modname)
            while parts:
                p = parts[0]
                s = f'{modname}.{p}'
                try:
                    mod = importlib.import_module(s)
                    parts.pop(0)
                    modname = s
                except ImportError:
                    break
        # if we reach this point, mod is the module, already imported, and
        # parts is the list of parts in the object hierarchy to be traversed, or
        # an empty list if just the module is wanted.
        result = mod
        for p in parts:
>           result = getattr(result, p)
                     ^^^^^^^^^^^^^^^^^^
E           AttributeError: module 'src' has no attribute 'ticket_master'

/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pkgutil.py:528: AttributeError
______ TestBulkOperationsPerformance.test_bulk_issue_creation_performance ______
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1393: in patched
    with self.decoration_helper(patched,
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/contextlib.py:137: in __enter__
    return next(self.gen)
           ^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1375: in decoration_helper
    arg = exit_stack.enter_context(patching)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/contextlib.py:526: in enter_context
    result = _enter(cm)
             ^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1451: in __enter__
    self.target = self.getter()
                  ^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

name = 'src.ticket_master.issue'

    def resolve_name(name):
        """
        Resolve a name to an object.
    
        It is expected that `name` will be a string in one of the following
        formats, where W is shorthand for a valid Python identifier and dot stands
        for a literal period in these pseudo-regexes:
    
        W(.W)*
        W(.W)*:(W(.W)*)?
    
        The first form is intended for backward compatibility only. It assumes that
        some part of the dotted name is a package, and the rest is an object
        somewhere within that package, possibly nested inside other objects.
        Because the place where the package stops and the object hierarchy starts
        can't be inferred by inspection, repeated attempts to import must be done
        with this form.
    
        In the second form, the caller makes the division point clear through the
        provision of a single colon: the dotted name to the left of the colon is a
        package to be imported, and the dotted name to the right is the object
        hierarchy within that package. Only one import is needed in this form. If
        it ends with the colon, then a module object is returned.
    
        The function will return an object (which might be a module), or raise one
        of the following exceptions:
    
        ValueError - if `name` isn't in a recognised format
        ImportError - if an import failed when it shouldn't have
        AttributeError - if a failure occurred when traversing the object hierarchy
                         within the imported package to get to the desired object.
        """
        global _NAME_PATTERN
        if _NAME_PATTERN is None:
            # Lazy import to speedup Python startup time
            import re
            dotted_words = r'(?!\d)(\w+)(\.(?!\d)(\w+))*'
            _NAME_PATTERN = re.compile(f'^(?P<pkg>{dotted_words})'
                                       f'(?P<cln>:(?P<obj>{dotted_words})?)?$',
                                       re.UNICODE)
    
        m = _NAME_PATTERN.match(name)
        if not m:
            raise ValueError(f'invalid format: {name!r}')
        gd = m.groupdict()
        if gd.get('cln'):
            # there is a colon - a one-step import is all that's needed
            mod = importlib.import_module(gd['pkg'])
            parts = gd.get('obj')
            parts = parts.split('.') if parts else []
        else:
            # no colon - have to iterate to find the package boundary
            parts = name.split('.')
            modname = parts.pop(0)
            # first part *must* be a module/package.
            mod = importlib.import_module(modname)
            while parts:
                p = parts[0]
                s = f'{modname}.{p}'
                try:
                    mod = importlib.import_module(s)
                    parts.pop(0)
                    modname = s
                except ImportError:
                    break
        # if we reach this point, mod is the module, already imported, and
        # parts is the list of parts in the object hierarchy to be traversed, or
        # an empty list if just the module is wanted.
        result = mod
        for p in parts:
>           result = getattr(result, p)
                     ^^^^^^^^^^^^^^^^^^
E           AttributeError: module 'src' has no attribute 'ticket_master'

/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pkgutil.py:528: AttributeError
_____________________ TestPipelineStep.test_execute_basic ______________________

self = <tests.test_pipe.TestPipelineStep testMethod=test_execute_basic>

    def test_execute_basic(self):
        """Test basic step execution."""
>       template = PromptTemplate(
            "test", PromptType.ISSUE_GENERATION, "Generate {count} issues"
        )
E       TypeError: PromptTemplate.__init__() missing 1 required positional argument: 'variables'

tests/test_pipe.py:73: TypeError
_________________ TestPipelineStep.test_execute_with_llm_error _________________

self = <tests.test_pipe.TestPipelineStep testMethod=test_execute_with_llm_error>

    def test_execute_with_llm_error(self):
        """Test step execution when LLM raises an error."""
>       template = PromptTemplate("test", PromptType.ISSUE_GENERATION, "Test")
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: PromptTemplate.__init__() missing 1 required positional argument: 'variables'

tests/test_pipe.py:121: TypeError
___________ TestPipelineStep.test_execute_with_validation_exception ____________

self = <tests.test_pipe.TestPipelineStep testMethod=test_execute_with_validation_exception>

    def test_execute_with_validation_exception(self):
        """Test step execution when validation function raises exception."""
>       template = PromptTemplate("test", PromptType.ISSUE_GENERATION, "Test")
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: PromptTemplate.__init__() missing 1 required positional argument: 'variables'

tests/test_pipe.py:134: TypeError
____________ TestPipelineStep.test_execute_with_validation_failure _____________

self = <tests.test_pipe.TestPipelineStep testMethod=test_execute_with_validation_failure>

    def test_execute_with_validation_failure(self):
        """Test step execution with failed validation."""
>       template = PromptTemplate("test", PromptType.ISSUE_GENERATION, "Test")
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: PromptTemplate.__init__() missing 1 required positional argument: 'variables'

tests/test_pipe.py:105: TypeError
____________ TestPipelineStep.test_execute_with_validation_success _____________

self = <tests.test_pipe.TestPipelineStep testMethod=test_execute_with_validation_success>

    def test_execute_with_validation_success(self):
        """Test step execution with successful validation."""
>       template = PromptTemplate("test", PromptType.ISSUE_GENERATION, "Test")
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: PromptTemplate.__init__() missing 1 required positional argument: 'variables'

tests/test_pipe.py:89: TypeError
__________________________ TestPipelineStep.test_init __________________________

self = <tests.test_pipe.TestPipelineStep testMethod=test_init>

    def test_init(self):
        """Test PipelineStep initialization."""
>       template = PromptTemplate(
            "test", PromptType.ISSUE_GENERATION, "Test {value}"
        )
E       TypeError: PromptTemplate.__init__() missing 1 required positional argument: 'variables'

tests/test_pipe.py:36: TypeError
_________________ TestPipelineStep.test_init_with_custom_stage _________________

self = <tests.test_pipe.TestPipelineStep testMethod=test_init_with_custom_stage>

    def test_init_with_custom_stage(self):
        """Test PipelineStep initialization with custom stage."""
>       template = PromptTemplate("test", PromptType.ISSUE_GENERATION, "Test")
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: PromptTemplate.__init__() missing 1 required positional argument: 'variables'

tests/test_pipe.py:48: TypeError
_____________ TestPipelineStep.test_init_with_validation_function ______________

self = <tests.test_pipe.TestPipelineStep testMethod=test_init_with_validation_function>

    def test_init_with_validation_function(self):
        """Test PipelineStep initialization with validation function."""
>       template = PromptTemplate("test", PromptType.ISSUE_GENERATION, "Test")
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: PromptTemplate.__init__() missing 1 required positional argument: 'variables'

tests/test_pipe.py:57: TypeError
_______________________ TestPipelineStep.test_str_method _______________________

self = <tests.test_pipe.TestPipelineStep testMethod=test_str_method>

    def test_str_method(self):
        """Test __str__ method."""
>       template = PromptTemplate("test", PromptType.ISSUE_GENERATION, "Test")
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: PromptTemplate.__init__() missing 1 required positional argument: 'variables'

tests/test_pipe.py:155: TypeError
____________________________ TestPipe.test_add_step ____________________________

self = <tests.test_pipe.TestPipe testMethod=test_add_step>

    def test_add_step(self):
        """Test adding steps to pipeline."""
>       pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: Pipe.__init__() takes 1 positional argument but 4 were given

tests/test_pipe.py:208: TypeError
____________________ TestPipe.test_add_step_duplicate_name _____________________

self = <tests.test_pipe.TestPipe testMethod=test_add_step_duplicate_name>

    def test_add_step_duplicate_name(self):
        """Test adding step with duplicate name."""
>       pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: Pipe.__init__() takes 1 positional argument but 4 were given

tests/test_pipe.py:234: TypeError
__________________ TestPipe.test_add_step_max_steps_exceeded ___________________

self = <tests.test_pipe.TestPipe testMethod=test_add_step_max_steps_exceeded>

    def test_add_step_max_steps_exceeded(self):
        """Test adding step when max steps is exceeded."""
>       pipe = Pipe(
            "test_pipeline",
            self.mock_input_llm,
            self.mock_output_llm,
            max_steps=1,
        )
E       TypeError: Pipe.__init__() got an unexpected keyword argument 'max_steps'

tests/test_pipe.py:244: TypeError
____________________ TestPipe.test_add_step_with_validation ____________________

self = <tests.test_pipe.TestPipe testMethod=test_add_step_with_validation>

    def test_add_step_with_validation(self):
        """Test adding step with validation function."""
>       pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: Pipe.__init__() takes 1 positional argument but 4 were given

tests/test_pipe.py:219: TypeError
__________________________ TestPipe.test_clear_steps ___________________________

self = <tests.test_pipe.TestPipe testMethod=test_clear_steps>

    def test_clear_steps(self):
        """Test clearing all steps."""
>       pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: Pipe.__init__() takes 1 positional argument but 4 were given

tests/test_pipe.py:413: TypeError
_____________________ TestPipe.test_execute_empty_pipeline _____________________

self = <tests.test_pipe.TestPipe testMethod=test_execute_empty_pipeline>

    def test_execute_empty_pipeline(self):
        """Test executing empty pipeline."""
>       pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: Pipe.__init__() takes 1 positional argument but 4 were given

tests/test_pipe.py:259: TypeError
_____________________ TestPipe.test_execute_multiple_steps _____________________

self = <tests.test_pipe.TestPipe testMethod=test_execute_multiple_steps>

    def test_execute_multiple_steps(self):
        """Test executing pipeline with multiple steps."""
>       pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: Pipe.__init__() takes 1 positional argument but 4 were given

tests/test_pipe.py:280: TypeError
______________________ TestPipe.test_execute_single_step _______________________

self = <tests.test_pipe.TestPipe testMethod=test_execute_single_step>

    def test_execute_single_step(self):
        """Test executing pipeline with single step."""
>       pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: Pipe.__init__() takes 1 positional argument but 4 were given

tests/test_pipe.py:266: TypeError
___________________ TestPipe.test_execute_with_step_failure ____________________

self = <tests.test_pipe.TestPipe testMethod=test_execute_with_step_failure>

    def test_execute_with_step_failure(self):
        """Test executing pipeline when step fails."""
>       pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: Pipe.__init__() takes 1 positional argument but 4 were given

tests/test_pipe.py:300: TypeError
_________________________ TestPipe.test_get_step_names _________________________

self = <tests.test_pipe.TestPipe testMethod=test_get_step_names>

    def test_get_step_names(self):
        """Test getting step names."""
>       pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: Pipe.__init__() takes 1 positional argument but 4 were given

tests/test_pipe.py:360: TypeError
_______________________ TestPipe.test_get_steps_by_stage _______________________

self = <tests.test_pipe.TestPipe testMethod=test_get_steps_by_stage>

    def test_get_steps_by_stage(self):
        """Test getting steps by stage."""
>       pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: Pipe.__init__() takes 1 positional argument but 4 were given

tests/test_pipe.py:371: TypeError
______________________________ TestPipe.test_init ______________________________

self = <tests.test_pipe.TestPipe testMethod=test_init>

    def test_init(self):
        """Test Pipe initialization."""
>       pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: Pipe.__init__() takes 1 positional argument but 4 were given

tests/test_pipe.py:186: TypeError
___________________ TestPipe.test_init_with_optional_params ____________________

self = <tests.test_pipe.TestPipe testMethod=test_init_with_optional_params>

    def test_init_with_optional_params(self):
        """Test Pipe initialization with optional parameters."""
>       pipe = Pipe(
            "test_pipeline",
            self.mock_input_llm,
            self.mock_output_llm,
            description="Test description",
            max_steps=10,
        )
E       TypeError: Pipe.__init__() got an unexpected keyword argument 'description'

tests/test_pipe.py:195: TypeError
___________________________ TestPipe.test_len_method ___________________________

self = <tests.test_pipe.TestPipe testMethod=test_len_method>

    def test_len_method(self):
        """Test __len__ method."""
>       pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: Pipe.__init__() takes 1 positional argument but 4 were given

tests/test_pipe.py:445: TypeError
__________________________ TestPipe.test_remove_step ___________________________

self = <tests.test_pipe.TestPipe testMethod=test_remove_step>

    def test_remove_step(self):
        """Test removing a step."""
>       pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: Pipe.__init__() takes 1 positional argument but 4 were given

tests/test_pipe.py:391: TypeError
____________________ TestPipe.test_remove_step_nonexistent _____________________

self = <tests.test_pipe.TestPipe testMethod=test_remove_step_nonexistent>

    def test_remove_step_nonexistent(self):
        """Test removing a non-existent step."""
>       pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: Pipe.__init__() takes 1 positional argument but 4 were given

tests/test_pipe.py:405: TypeError
__________________________ TestPipe.test_repr_method ___________________________

self = <tests.test_pipe.TestPipe testMethod=test_repr_method>

    def test_repr_method(self):
        """Test __repr__ method."""
>       pipe = Pipe(
            "test_pipeline",
            self.mock_input_llm,
            self.mock_output_llm,
            description="Test description",
        )
E       TypeError: Pipe.__init__() got an unexpected keyword argument 'description'

tests/test_pipe.py:463: TypeError
___________________________ TestPipe.test_str_method ___________________________

self = <tests.test_pipe.TestPipe testMethod=test_str_method>

    def test_str_method(self):
        """Test __str__ method."""
>       pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: Pipe.__init__() takes 1 positional argument but 4 were given

tests/test_pipe.py:455: TypeError
____________________________ TestPipe.test_to_dict _____________________________

self = <tests.test_pipe.TestPipe testMethod=test_to_dict>

    def test_to_dict(self):
        """Test converting pipeline to dictionary."""
>       pipe = Pipe(
            "test_pipeline",
            self.mock_input_llm,
            self.mock_output_llm,
            description="Test description",
        )
E       TypeError: Pipe.__init__() got an unexpected keyword argument 'description'

tests/test_pipe.py:425: TypeError
_______________________ TestPipe.test_validate_pipeline ________________________

self = <tests.test_pipe.TestPipe testMethod=test_validate_pipeline>

    def test_validate_pipeline(self):
        """Test pipeline validation."""
>       pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: Pipe.__init__() takes 1 positional argument but 4 were given

tests/test_pipe.py:315: TypeError
_____________ TestPipe.test_validate_pipeline_missing_input_stage ______________

self = <tests.test_pipe.TestPipe testMethod=test_validate_pipeline_missing_input_stage>

    def test_validate_pipeline_missing_input_stage(self):
        """Test validation when INPUT stage is missing."""
>       pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: Pipe.__init__() takes 1 positional argument but 4 were given

tests/test_pipe.py:336: TypeError
_____________ TestPipe.test_validate_pipeline_missing_output_stage _____________

self = <tests.test_pipe.TestPipe testMethod=test_validate_pipeline_missing_output_stage>

    def test_validate_pipeline_missing_output_stage(self):
        """Test validation when OUTPUT stage is missing."""
>       pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: Pipe.__init__() takes 1 positional argument but 4 were given

tests/test_pipe.py:349: TypeError
__________________ TestPipe.test_validate_pipeline_with_steps __________________

self = <tests.test_pipe.TestPipe testMethod=test_validate_pipeline_with_steps>

    def test_validate_pipeline_with_steps(self):
        """Test pipeline validation with valid steps."""
>       pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: Pipe.__init__() takes 1 positional argument but 4 were given

tests/test_pipe.py:323: TypeError
_____________________ TestPipeStage.test_pipe_stage_values _____________________

self = <tests.test_pipe.TestPipeStage testMethod=test_pipe_stage_values>

    def test_pipe_stage_values(self):
        """Test PipeStage enum values."""
>       self.assertEqual(PipeStage.INPUT.value, "input")
                         ^^^^^^^^^^^^^^^
E       AttributeError: type object 'PipeStage' has no attribute 'INPUT'

tests/test_pipe.py:499: AttributeError
________________ TestPromptTemplate.test_get_required_variables ________________

self = <tests.test_prompt.TestPromptTemplate testMethod=test_get_required_variables>

    def test_get_required_variables(self):
        """Test extraction of required variables."""
>       template = PromptTemplate(
            name="test_template",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Generate {num_issues} issues for {repo_name} in {language}",
        )
E       TypeError: PromptTemplate.__init__() got an unexpected keyword argument 'base_template'

tests/test_prompt.py:74: TypeError
_______________ TestPromptTemplate.test_init_string_prompt_type ________________

self = <tests.test_prompt.TestPromptTemplate testMethod=test_init_string_prompt_type>

    def test_init_string_prompt_type(self):
        """Test PromptTemplate initialization with string prompt type."""
>       template = PromptTemplate(
            name="test_template",
            prompt_type="issue_generation",
        )
E       TypeError: PromptTemplate.__init__() missing 2 required positional arguments: 'template' and 'variables'

tests/test_prompt.py:40: TypeError
_________________ TestPromptTemplate.test_init_valid_template __________________

self = <tests.test_prompt.TestPromptTemplate testMethod=test_init_valid_template>

    def test_init_valid_template(self):
        """Test PromptTemplate initialization with valid data."""
>       template = PromptTemplate(
            name="test_template",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Generate {num_issues} issues for {repo_name}",
        )
E       TypeError: PromptTemplate.__init__() got an unexpected keyword argument 'base_template'

tests/test_prompt.py:25: TypeError
_________________ TestPromptTemplate.test_provider_variations __________________

self = <tests.test_prompt.TestPromptTemplate testMethod=test_provider_variations>

    def test_provider_variations(self):
        """Test provider-specific template variations."""
>       template = PromptTemplate(
            name="test_template",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Base: {value}",
            provider_variations={
                "ollama": "Ollama: {value}",
                "openai": "OpenAI: {value}",
            },
        )
E       TypeError: PromptTemplate.__init__() got an unexpected keyword argument 'base_template'

tests/test_prompt.py:87: TypeError
_____________________ TestPromptTemplate.test_render_basic _____________________

self = <tests.test_prompt.TestPromptTemplate testMethod=test_render_basic>

    def test_render_basic(self):
        """Test basic template rendering."""
>       template = PromptTemplate(
            name="test_template",
            prompt_type=PromptType.ISSUE_GENERATION,
        )
E       TypeError: PromptTemplate.__init__() missing 2 required positional arguments: 'template' and 'variables'

tests/test_prompt.py:49: TypeError
_______________ TestPromptTemplate.test_render_missing_variable ________________

self = <tests.test_prompt.TestPromptTemplate testMethod=test_render_missing_variable>

    def test_render_missing_variable(self):
        """Test template rendering with missing variable."""
>       template = PromptTemplate(
            name="test_template",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Generate {num_issues} issues for {repo_name}",
        )
E       TypeError: PromptTemplate.__init__() got an unexpected keyword argument 'base_template'

tests/test_prompt.py:61: TypeError
_________________________ TestPrompt.test_add_template _________________________

self = <tests.test_prompt.TestPrompt testMethod=test_add_template>

    def setUp(self):
        """Set up test prompt container."""
>       self.prompt = Prompt(default_provider="ollama")
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: Prompt.__init__() got an unexpected keyword argument 'default_provider'

tests/test_prompt.py:116: TypeError
___________________ TestPrompt.test_create_builtin_templates ___________________

self = <tests.test_prompt.TestPrompt testMethod=test_create_builtin_templates>

    def setUp(self):
        """Set up test prompt container."""
>       self.prompt = Prompt(default_provider="ollama")
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: Prompt.__init__() got an unexpected keyword argument 'default_provider'

tests/test_prompt.py:116: TypeError
_________________________ TestPrompt.test_get_template _________________________

self = <tests.test_prompt.TestPrompt testMethod=test_get_template>

    def setUp(self):
        """Set up test prompt container."""
>       self.prompt = Prompt(default_provider="ollama")
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: Prompt.__init__() got an unexpected keyword argument 'default_provider'

tests/test_prompt.py:116: TypeError
_____________________________ TestPrompt.test_init _____________________________

self = <tests.test_prompt.TestPrompt testMethod=test_init>

    def setUp(self):
        """Set up test prompt container."""
>       self.prompt = Prompt(default_provider="ollama")
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: Prompt.__init__() got an unexpected keyword argument 'default_provider'

tests/test_prompt.py:116: TypeError
________________________ TestPrompt.test_list_templates ________________________

self = <tests.test_prompt.TestPrompt testMethod=test_list_templates>

    def setUp(self):
        """Set up test prompt container."""
>       self.prompt = Prompt(default_provider="ollama")
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: Prompt.__init__() got an unexpected keyword argument 'default_provider'

tests/test_prompt.py:116: TypeError
_______________________ TestPrompt.test_render_template ________________________

self = <tests.test_prompt.TestPrompt testMethod=test_render_template>

    def setUp(self):
        """Set up test prompt container."""
>       self.prompt = Prompt(default_provider="ollama")
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: Prompt.__init__() got an unexpected keyword argument 'default_provider'

tests/test_prompt.py:116: TypeError
_____________________ TestPullRequest.test_get_branch_info _____________________

self = <tests.test_pull_request.TestPullRequest testMethod=test_get_branch_info>

    def test_get_branch_info(self):
        """Test getting branch information."""
        pr = PullRequest(self.mock_pr)
    
>       self.assertEqual(pr.source_branch, "feature-branch")
                         ^^^^^^^^^^^^^^^^
E       AttributeError: 'PullRequest' object has no attribute 'source_branch'

tests/test_pull_request.py:84: AttributeError
____________________ TestPullRequest.test_get_changed_files ____________________

self = <tests.test_pull_request.TestPullRequest testMethod=test_get_changed_files>

    def test_get_changed_files(self):
        """Test getting changed files from pull request."""
        # Mock file changes
        mock_file1 = Mock()
        mock_file1.filename = "file1.py"
        mock_file1.status = "modified"
        mock_file1.additions = 10
        mock_file1.deletions = 5
        mock_file1.changes = 15
        mock_file1.patch = "@@ -1,3 +1,4 @@\n+added line\n original line"
    
        mock_file2 = Mock()
        mock_file2.filename = "file2.py"
        mock_file2.status = "added"
        mock_file2.additions = 20
        mock_file2.deletions = 0
        mock_file2.changes = 20
        mock_file2.patch = "@@ -0,0 +1,5 @@\n+new file content"
    
        self.mock_pr.get_files.return_value = [mock_file1, mock_file2]
    
        pr = PullRequest(self.mock_pr)
        files = pr.changed_files
>       self.assertEqual(len(files), 2)
                         ^^^^^^^^^^
E       TypeError: object of type 'int' has no len()

tests/test_pull_request.py:216: TypeError
_________________ TestPullRequest.test_get_changed_files_error _________________

self = <tests.test_pull_request.TestPullRequest testMethod=test_get_changed_files_error>

    def test_get_changed_files_error(self):
        """Test get_changed_files with error."""
        self.mock_pr.get_files.side_effect = Exception("API Error")
    
        pr = PullRequest(self.mock_pr)
    
        with self.assertRaises(PullRequestError):
>           pr.get_changed_files()
            ^^^^^^^^^^^^^^^^^^^^
E           AttributeError: 'PullRequest' object has no attribute 'get_changed_files'. Did you mean: 'changed_files'?

tests/test_pull_request.py:229: AttributeError
______________________ TestPullRequest.test_get_comments _______________________

self = <tests.test_pull_request.TestPullRequest testMethod=test_get_comments>

    def test_get_comments(self):
        """Test getting comments from pull request."""
        # Mock comments
        mock_comment1 = Mock()
        mock_comment1.id = 1
        mock_comment1.user.login = "commenter1"
        mock_comment1.user.name = "Commenter One"
        mock_comment1.body = "This is a comment"
        mock_comment1.created_at = datetime(2023, 1, 2, 10, 0, 0)
        mock_comment1.updated_at = datetime(2023, 1, 2, 10, 0, 0)
    
        mock_comment2 = Mock()
        mock_comment2.id = 2
        mock_comment2.user.login = "commenter2"
        mock_comment2.user.name = "Commenter Two"
        mock_comment2.body = "Another comment"
        mock_comment2.created_at = datetime(2023, 1, 2, 11, 0, 0)
        mock_comment2.updated_at = datetime(2023, 1, 2, 11, 30, 0)
    
        self.mock_pr.get_issue_comments.return_value = [
            mock_comment1,
            mock_comment2,
        ]
    
        pr = PullRequest(self.mock_pr)
>       comments = pr.get_comments()
                   ^^^^^^^^^^^^^^^
E       AttributeError: 'PullRequest' object has no attribute 'get_comments'. Did you mean: 'get_commits'?

tests/test_pull_request.py:294: AttributeError
___________________ TestPullRequest.test_get_comments_error ____________________

self = <tests.test_pull_request.TestPullRequest testMethod=test_get_comments_error>

    def test_get_comments_error(self):
        """Test get_comments with error."""
        self.mock_pr.get_issue_comments.side_effect = Exception("API Error")
    
        pr = PullRequest(self.mock_pr)
    
        with self.assertRaises(PullRequestError):
>           pr.get_comments()
            ^^^^^^^^^^^^^^^
E           AttributeError: 'PullRequest' object has no attribute 'get_comments'. Did you mean: 'get_commits'?

tests/test_pull_request.py:309: AttributeError
____________________ TestPullRequest.test_get_commits_error ____________________

    def get_commits(self) -> List[Any]:
        """Get commits from the pull request."""
        try:
            if self.pr_obj and hasattr(self.pr_obj, "get_commits"):
                commits = []
>               for commit in self.pr_obj.get_commits():
                              ^^^^^^^^^^^^^^^^^^^^^^^^^

src/ticket_master_consolidated.py:797: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1139: in __call__
    return self._mock_call(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1143: in _mock_call
    return self._execute_mock_call(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <Mock name='mock.get_commits' id='4483797680'>, args = (), kwargs = {}
effect = Exception('API Error')

    def _execute_mock_call(self, /, *args, **kwargs):
        # separate from _increment_mock_call so that awaited functions are
        # executed separately from their call, also AsyncMock overrides this method
    
        effect = self.side_effect
        if effect is not None:
            if _is_exception(effect):
>               raise effect
E               Exception: API Error

/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1198: Exception

During handling of the above exception, another exception occurred:

self = <tests.test_pull_request.TestPullRequest testMethod=test_get_commits_error>

    def test_get_commits_error(self):
        """Test get_commits with error."""
        self.mock_pr.get_commits.side_effect = Exception("API Error")
    
        pr = PullRequest(self.mock_pr)
    
        with self.assertRaises(PullRequestError):
>           pr.get_commits()

tests/test_pull_request.py:191: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

    def get_commits(self) -> List[Any]:
        """Get commits from the pull request."""
        try:
            if self.pr_obj and hasattr(self.pr_obj, "get_commits"):
                commits = []
                for commit in self.pr_obj.get_commits():
                    # Create a simple object with the expected attributes
                    class CommitInfo:
                        def __init__(
                            self,
                            sha,
                            message,
                            author_name,
                            author_email,
                            author_date,
                        ):
                            self.hash = sha
                            self.message = message
                            self.author_name = author_name
                            self.author_email = author_email
                            self.author_date = author_date
    
                    commit_info = CommitInfo(
                        commit.sha,
                        commit.commit.message,
                        commit.commit.author.name,
                        commit.commit.author.email,
                        (
                            commit.commit.author.date.isoformat()
                            if commit.commit.author.date
                            else None
                        ),
                    )
                    commits.append(commit_info)
                return commits
            else:
                return []
        except Exception as e:
>           raise Exception(f"Failed to get commits: {e}")
E           Exception: Failed to get commits: API Error

src/ticket_master_consolidated.py:830: Exception
____________________ TestPullRequest.test_get_reviews_error ____________________

    def get_reviews(self) -> List[Dict[str, Any]]:
        """Get reviews from the pull request."""
        try:
            if self.pr_obj and hasattr(self.pr_obj, "get_reviews"):
                reviews = []
>               for review in self.pr_obj.get_reviews():
                              ^^^^^^^^^^^^^^^^^^^^^^^^^

src/ticket_master_consolidated.py:837: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1139: in __call__
    return self._mock_call(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1143: in _mock_call
    return self._execute_mock_call(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <Mock name='mock.get_reviews' id='4484109936'>, args = (), kwargs = {}
effect = Exception('API Error')

    def _execute_mock_call(self, /, *args, **kwargs):
        # separate from _increment_mock_call so that awaited functions are
        # executed separately from their call, also AsyncMock overrides this method
    
        effect = self.side_effect
        if effect is not None:
            if _is_exception(effect):
>               raise effect
E               Exception: API Error

/opt/homebrew/Cellar/python@3.12/3.12.11_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py:1198: Exception

During handling of the above exception, another exception occurred:

self = <tests.test_pull_request.TestPullRequest testMethod=test_get_reviews_error>

    def test_get_reviews_error(self):
        """Test get_reviews with error."""
        self.mock_pr.get_reviews.side_effect = Exception("API Error")
    
        pr = PullRequest(self.mock_pr)
    
        with self.assertRaises(PullRequestError):
>           pr.get_reviews()

tests/test_pull_request.py:267: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

    def get_reviews(self) -> List[Dict[str, Any]]:
        """Get reviews from the pull request."""
        try:
            if self.pr_obj and hasattr(self.pr_obj, "get_reviews"):
                reviews = []
                for review in self.pr_obj.get_reviews():
                    reviews.append(
                        {
                            "id": review.id,
                            "reviewer": review.user.login,  # Test expects "reviewer" key
                            "user": {
                                "login": review.user.login,
                                "name": review.user.name,
                            },
                            "state": review.state,
                            "body": review.body,
                            "submitted_at": (
                                review.submitted_at.isoformat()
                                if review.submitted_at
                                else None
                            ),
                        }
                    )
                return reviews
            else:
                return []
        except Exception as e:
>           raise Exception(f"Failed to get reviews: {e}")
E           Exception: Failed to get reviews: API Error

src/ticket_master_consolidated.py:859: Exception
_______________ TestPullRequest.test_is_approved_with_approvals ________________

self = <tests.test_pull_request.TestPullRequest testMethod=test_is_approved_with_approvals>

    def test_is_approved_with_approvals(self):
        """Test is_approved when PR has approvals."""
        # Mock reviews with approvals
        mock_review1 = Mock()
        mock_review1.state = "APPROVED"
        mock_review2 = Mock()
        mock_review2.state = "COMMENTED"
    
        self.mock_pr.get_reviews.return_value = [mock_review1, mock_review2]
    
        pr = PullRequest(self.mock_pr)
    
>       self.assertTrue(pr.is_approved())
E       AssertionError: False is not true

tests/test_pull_request.py:347: AssertionError
___________________ TestRepository.test_get_repository_info ____________________

self = <tests.test_repository.TestRepository object at 0x10abcde50>
temp_git_repo = '/var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmpu5m08qa3/test_repo'

    def test_get_repository_info(self, temp_git_repo):
        """Test getting repository information."""
        repo = Repository(temp_git_repo)
        info = repo.get_repository_info()
    
        assert isinstance(info, dict)
        required_keys = [
            "path",
            "name",
            "active_branch",
            "total_commits",
            "branches",
            "is_dirty",
        ]
        for key in required_keys:
>           assert key in info
E           AssertionError: assert 'total_commits' in {'active_branch': 'master', 'head_commit': '0da205fe', 'is_bare': False, 'name': 'test_repo', ...}

tests/test_repository.py:109: AssertionError
---------------------------- Captured stdout setup -----------------------------
Initialized empty Git repository in /private/var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmpu5m08qa3/test_repo/.git/
[master (root-commit) 0da205f] Initial commit
 1 file changed, 1 insertion(+)
 create mode 100644 README.md
----------------------------- Captured stdout call -----------------------------
2025-09-30 00:00:18 - Repository - INFO - Initialized repository at /private/var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmpu5m08qa3/test_repo
2025-09-30 00:00:18 - Repository - INFO - Initialized repository at /private/var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmpu5m08qa3/test_repo
2025-09-30 00:00:18 - Repository - INFO - Initialized repository at /private/var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmpu5m08qa3/test_repo
------------------------------ Captured log call -------------------------------
INFO     Repository:ticket_master_consolidated.py:879 Initialized repository at /private/var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmpu5m08qa3/test_repo
___________________ TestRepository.test_repr_representation ____________________

self = <tests.test_repository.TestRepository object at 0x10abce630>
temp_git_repo = '/var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmp5tia4ez8/test_repo'

    def test_repr_representation(self, temp_git_repo):
        """Test detailed string representation of Repository."""
        repo = Repository(temp_git_repo)
        repr_str = repr(repo)
    
        assert "Repository(" in repr_str
        assert "path=" in repr_str
>       assert "active_branch=" in repr_str
E       assert 'active_branch=' in "Repository(path='/private/var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmp5tia4ez8/test_repo', branch='master', head='0da205fe')"

tests/test_repository.py:180: AssertionError
---------------------------- Captured stdout setup -----------------------------
Initialized empty Git repository in /private/var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmp5tia4ez8/test_repo/.git/
[master (root-commit) 0da205f] Initial commit
 1 file changed, 1 insertion(+)
 create mode 100644 README.md
----------------------------- Captured stdout call -----------------------------
2025-09-30 00:00:18 - Repository - INFO - Initialized repository at /private/var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmp5tia4ez8/test_repo
2025-09-30 00:00:18 - Repository - INFO - Initialized repository at /private/var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmp5tia4ez8/test_repo
2025-09-30 00:00:18 - Repository - INFO - Initialized repository at /private/var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmp5tia4ez8/test_repo
------------------------------ Captured log call -------------------------------
INFO     Repository:ticket_master_consolidated.py:879 Initialized repository at /private/var/folders/zd/qd5flt2j43722srmc5kg9f6h0000gn/T/tmp5tia4ez8/test_repo
================================ tests coverage ================================
______________ coverage: platform darwin, python 3.12.11-final-0 _______________

Name                                                                                                                             Stmts   Miss  Cover
----------------------------------------------------------------------------------------------------------------------------------------------------
/opt/homebrew/Cellar/certifi/2025.8.3/lib/python3.12/site-packages/certifi/__init__.py                                               3      0   100%
/opt/homebrew/Cellar/certifi/2025.8.3/lib/python3.12/site-packages/certifi/core.py                                                  27     13    52%
/opt/homebrew/Cellar/cryptography/46.0.1/lib/python3.12/site-packages/cryptography/__about__.py                                      5      0   100%
/opt/homebrew/Cellar/cryptography/46.0.1/lib/python3.12/site-packages/cryptography/__init__.py                                       3      0   100%
/opt/homebrew/Cellar/cryptography/46.0.1/lib/python3.12/site-packages/cryptography/exceptions.py                                    24      4    83%
/opt/homebrew/Cellar/cryptography/46.0.1/lib/python3.12/site-packages/cryptography/hazmat/__init__.py                                2      0   100%
/opt/homebrew/Cellar/cryptography/46.0.1/lib/python3.12/site-packages/cryptography/hazmat/_oid.py                                  160      0   100%
/opt/homebrew/Cellar/cryptography/46.0.1/lib/python3.12/site-packages/cryptography/hazmat/backends/__init__.py                       5      2    60%
/opt/homebrew/Cellar/cryptography/46.0.1/lib/python3.12/site-packages/cryptography/hazmat/bindings/__init__.py                       0      0   100%
/opt/homebrew/Cellar/cryptography/46.0.1/lib/python3.12/site-packages/cryptography/hazmat/decrepit/__init__.py                       1      0   100%
/opt/homebrew/Cellar/cryptography/46.0.1/lib/python3.12/site-packages/cryptography/hazmat/decrepit/ciphers/__init__.py               1      0   100%
/opt/homebrew/Cellar/cryptography/46.0.1/lib/python3.12/site-packages/cryptography/hazmat/decrepit/ciphers/algorithms.py            70     18    74%
/opt/homebrew/Cellar/cryptography/46.0.1/lib/python3.12/site-packages/cryptography/hazmat/primitives/__init__.py                     0      0   100%
/opt/homebrew/Cellar/cryptography/46.0.1/lib/python3.12/site-packages/cryptography/hazmat/primitives/_asymmetric.py                  6      0   100%
/opt/homebrew/Cellar/cryptography/46.0.1/lib/python3.12/site-packages/cryptography/hazmat/primitives/_cipheralgorithm.py            23      4    83%
/opt/homebrew/Cellar/cryptography/46.0.1/lib/python3.12/site-packages/cryptography/hazmat/primitives/_serialization.py              79     35    56%
/opt/homebrew/Cellar/cryptography/46.0.1/lib/python3.12/site-packages/cryptography/hazmat/primitives/asymmetric/__init__.py          0      0   100%
/opt/homebrew/Cellar/cryptography/46.0.1/lib/python3.12/site-packages/cryptography/hazmat/primitives/asymmetric/dsa.py              60      5    92%
/opt/homebrew/Cellar/cryptography/46.0.1/lib/python3.12/site-packages/cryptography/hazmat/primitives/asymmetric/ec.py              198     22    89%
/opt/homebrew/Cellar/cryptography/46.0.1/lib/python3.12/site-packages/cryptography/hazmat/primitives/asymmetric/ed448.py            50     12    76%
/opt/homebrew/Cellar/cryptography/46.0.1/lib/python3.12/site-packages/cryptography/hazmat/primitives/asymmetric/ed25519.py          48     12    75%
/opt/homebrew/Cellar/cryptography/46.0.1/lib/python3.12/site-packages/cryptography/hazmat/primitives/asymmetric/padding.py          54     23    57%
/opt/homebrew/Cellar/cryptography/46.0.1/lib/python3.12/site-packages/cryptography/hazmat/primitives/asymmetric/rsa.py             111     53    52%
/opt/homebrew/Cellar/cryptography/46.0.1/lib/python3.12/site-packages/cryptography/hazmat/primitives/asymmetric/utils.py            14      5    64%
/opt/homebrew/Cellar/cryptography/46.0.1/lib/python3.12/site-packages/cryptography/hazmat/primitives/ciphers/__init__.py             4      0   100%
/opt/homebrew/Cellar/cryptography/46.0.1/lib/python3.12/site-packages/cryptography/hazmat/primitives/ciphers/algorithms.py          68     15    78%
/opt/homebrew/Cellar/cryptography/46.0.1/lib/python3.12/site-packages/cryptography/hazmat/primitives/ciphers/base.py                47     12    74%
/opt/homebrew/Cellar/cryptography/46.0.1/lib/python3.12/site-packages/cryptography/hazmat/primitives/ciphers/modes.py              140     59    58%
/opt/homebrew/Cellar/cryptography/46.0.1/lib/python3.12/site-packages/cryptography/hazmat/primitives/hashes.py                     129     20    84%
/opt/homebrew/Cellar/cryptography/46.0.1/lib/python3.12/site-packages/cryptography/hazmat/primitives/serialization/__init__.py       5      0   100%
/opt/homebrew/Cellar/cryptography/46.0.1/lib/python3.12/site-packages/cryptography/hazmat/primitives/serialization/base.py           7      0   100%
/opt/homebrew/Cellar/cryptography/46.0.1/lib/python3.12/site-packages/cryptography/hazmat/primitives/serialization/ssh.py          793    627    21%
/opt/homebrew/Cellar/cryptography/46.0.1/lib/python3.12/site-packages/cryptography/utils.py                                         79     29    63%
/opt/homebrew/Cellar/python-setuptools/80.9.0/lib/python3.12/site-packages/_distutils_hack/__init__.py                             101     96     5%
app.py                                                                                                                              98     30    69%
main.py                                                                                                                            443    213    52%
src/ticket_master_consolidated.py                                                                                                 1125    345    69%
tests/__init__.py                                                                                                                    0      0   100%
tests/test_app.py                                                                                                                  255      2    99%
tests/test_auth.py                                                                                                                 183     12    93%
tests/test_branch.py                                                                                                                62      1    98%
tests/test_colors.py                                                                                                               309     18    94%
tests/test_commit.py                                                                                                               184     11    94%
tests/test_data_scraper.py                                                                                                         263    131    50%
tests/test_database.py                                                                                                              52     19    63%
tests/test_edge_cases.py                                                                                                           156    105    33%
tests/test_examples.py                                                                                                             190     27    86%
tests/test_git_objects.py                                                                                                          374     54    86%
tests/test_github_utils.py                                                                                                         284     47    83%
tests/test_init.py                                                                                                                  64      1    98%
tests/test_integration.py                                                                                                           54      3    94%
tests/test_issue.py                                                                                                                674    181    73%
tests/test_llm.py                                                                                                                  361    146    60%
tests/test_main.py                                                                                                                 211     22    90%
tests/test_new_classes.py                                                                                                          276    127    54%
tests/test_ollama_tools.py                                                                                                         372    260    30%
tests/test_performance.py                                                                                                          220     70    68%
tests/test_pipe.py                                                                                                                 259    162    37%
tests/test_prompt.py                                                                                                                73     46    37%
tests/test_pull_request.py                                                                                                         304     11    96%
tests/test_repository.py                                                                                                           133      4    97%
----------------------------------------------------------------------------------------------------------------------------------------------------
TOTAL                                                                                                                             9296   3114    67%
=========================== short test summary info ============================
FAILED tests/test_app.py::TestGenerateIssuesRoute::test_generate_issues_with_local_path
FAILED tests/test_app.py::TestGenerateIssuesRoute::test_generate_issues_success_public_repo
FAILED tests/test_auth.py::TestAuthenticationGitHubIntegration::test_create_client_with_token
FAILED tests/test_auth.py::TestAuthenticationGitHubIntegration::test_create_client_token_parameter_overrides_instance
FAILED tests/test_auth.py::TestAuthenticationGitHubIntegration::test_is_authenticated_success
FAILED tests/test_auth.py::TestAuthenticationGitHubIntegration::test_get_user_info
FAILED tests/test_auth.py::TestAuthenticationGitHubIntegration::test_test_connection_success
FAILED tests/test_auth.py::TestAuthenticationErrorHandling::test_github_auth_error_inheritance
FAILED tests/test_colors.py::TestSupportsColor::test_supports_color_force_color_env
FAILED tests/test_colors.py::TestColorize::test_colorize_with_colors_enabled
FAILED tests/test_colors.py::TestColorize::test_colorize_only_style - TypeErr...
FAILED tests/test_colors.py::TestFormattingFunctions::test_success_function_bold
FAILED tests/test_colors.py::TestFormattingFunctions::test_error_function - A...
FAILED tests/test_colors.py::TestFormattingFunctions::test_error_function_bold
FAILED tests/test_colors.py::TestFormattingFunctions::test_warning_function_bold
FAILED tests/test_colors.py::TestFormattingFunctions::test_info_function_bold
FAILED tests/test_colors.py::TestFormattingFunctions::test_header_function_default
FAILED tests/test_colors.py::TestFormattingFunctions::test_header_function_custom_color
FAILED tests/test_colors.py::TestFormattingFunctions::test_highlight_function_default
FAILED tests/test_colors.py::TestFormattingFunctions::test_highlight_function_custom_color
FAILED tests/test_colors.py::TestProgressBar::test_progress_bar_zero_total - ...
FAILED tests/test_colors.py::TestProgressBar::test_progress_bar_full_completion
FAILED tests/test_colors.py::TestProgressBar::test_progress_bar_half_completion
FAILED tests/test_colors.py::TestProgressBar::test_progress_bar_custom_color
FAILED tests/test_colors.py::TestProgressBar::test_progress_bar_custom_width
FAILED tests/test_colors.py::TestProgressBar::test_progress_bar_colors_disabled
FAILED tests/test_colors.py::TestPrintColored::test_print_colored_basic - Ass...
FAILED tests/test_colors.py::TestFormattingFunctionsColorsDisabled::test_all_formatting_functions_colors_disabled
FAILED tests/test_colors.py::TestEdgeCases::test_empty_string_formatting - As...
FAILED tests/test_colors.py::TestEdgeCases::test_progress_bar_edge_cases - As...
FAILED tests/test_commit.py::TestCommit::test_init_invalid_commit - Attribute...
FAILED tests/test_data_scraper.py::TestDataScraper::test_analyze_activity_patterns
FAILED tests/test_data_scraper.py::TestDataScraper::test_analyze_code_quality
FAILED tests/test_data_scraper.py::TestDataScraper::test_init_invalid_repository_error
FAILED tests/test_data_scraper.py::TestDataScraper::test_init_with_cache_enabled
FAILED tests/test_data_scraper.py::TestDataScraper::test_init_with_cache_failure
FAILED tests/test_data_scraper.py::TestDataScraper::test_scrape_all - Attribu...
FAILED tests/test_data_scraper.py::TestDataScraper::test_scrape_build_configuration
FAILED tests/test_data_scraper.py::TestDataScraper::test_scrape_content_analysis
FAILED tests/test_data_scraper.py::TestDataScraper::test_scrape_dependencies
FAILED tests/test_data_scraper.py::TestDataScraper::test_scrape_file_structure
FAILED tests/test_data_scraper.py::TestDataScraper::test_scrape_git_history
FAILED tests/test_data_scraper.py::TestDataScraper::test_scrape_repository_info
FAILED tests/test_data_scraper.py::TestDataScraperCaching::test_get_from_cache_no_cache_db
FAILED tests/test_data_scraper.py::TestDataScraperCaching::test_get_from_cache_with_db
FAILED tests/test_data_scraper.py::TestDataScraperCaching::test_store_in_cache_no_cache_db
FAILED tests/test_data_scraper.py::TestDataScraperCaching::test_store_in_cache_with_db
FAILED tests/test_data_scraper.py::TestDataScraperPrivateMethods::test_analyze_branches
FAILED tests/test_data_scraper.py::TestDataScraperPrivateMethods::test_analyze_commits
FAILED tests/test_data_scraper.py::TestDataScraperPrivateMethods::test_analyze_contributors
FAILED tests/test_data_scraper.py::TestDataScraperPrivateMethods::test_calculate_repository_size
FAILED tests/test_data_scraper.py::TestDataScraperPrivateMethods::test_extract_git_config
FAILED tests/test_data_scraper.py::TestDataScraperPrivateMethods::test_extract_remote_info
FAILED tests/test_data_scraper.py::TestDataScraperPrivateMethods::test_scrape_repository_info_detailed
FAILED tests/test_data_scraper.py::TestDataScraperDependencyAnalysis::test_extract_go_dependencies
FAILED tests/test_data_scraper.py::TestDataScraperDependencyAnalysis::test_extract_java_dependencies_with_pom
FAILED tests/test_data_scraper.py::TestDataScraperDependencyAnalysis::test_extract_javascript_dependencies_invalid_json
FAILED tests/test_data_scraper.py::TestDataScraperDependencyAnalysis::test_extract_javascript_dependencies_with_package_json
FAILED tests/test_data_scraper.py::TestDataScraperDependencyAnalysis::test_extract_python_dependencies_no_file
FAILED tests/test_data_scraper.py::TestDataScraperDependencyAnalysis::test_extract_python_dependencies_with_requirements
FAILED tests/test_data_scraper.py::TestDataScraperDependencyAnalysis::test_extract_rust_dependencies
FAILED tests/test_data_scraper.py::TestDataScraperStringMethods::test_repr_method
FAILED tests/test_data_scraper.py::TestDataScraperStringMethods::test_str_method
FAILED tests/test_database.py::TestUserDatabase::test_cache_repository_data
FAILED tests/test_database.py::TestUserDatabase::test_connect_disconnect - As...
FAILED tests/test_database.py::TestUserDatabase::test_context_manager - TypeE...
FAILED tests/test_database.py::TestUserDatabase::test_create_tables - TypeErr...
FAILED tests/test_database.py::TestUserDatabase::test_user_preferences - Type...
FAILED tests/test_edge_cases.py::TestEdgeCases::test_empty_string_handling - ...
FAILED tests/test_edge_cases.py::TestEdgeCases::test_none_value_handling - Mo...
FAILED tests/test_edge_cases.py::TestEdgeCases::test_unicode_handling - Modul...
FAILED tests/test_edge_cases.py::TestEdgeCases::test_very_long_strings - Modu...
FAILED tests/test_edge_cases.py::TestEdgeCases::test_multiline_strings - Modu...
FAILED tests/test_edge_cases.py::TestEdgeCases::test_special_characters - Mod...
FAILED tests/test_edge_cases.py::TestErrorConditions::test_stdout_without_isatty
FAILED tests/test_edge_cases.py::TestErrorConditions::test_empty_term_environment
FAILED tests/test_edge_cases.py::TestErrorConditions::test_progress_bar_edge_values
FAILED tests/test_edge_cases.py::TestErrorConditions::test_color_constants_immutability
FAILED tests/test_edge_cases.py::TestErrorConditions::test_global_color_variables
FAILED tests/test_edge_cases.py::TestModuleStructure::test_colors_module_has_required_exports
FAILED tests/test_edge_cases.py::TestModuleStructure::test_colors_module_has_required_constants
FAILED tests/test_edge_cases.py::TestFunctionDefaults::test_colorize_defaults
FAILED tests/test_edge_cases.py::TestFunctionDefaults::test_formatting_function_defaults
FAILED tests/test_edge_cases.py::TestFunctionDefaults::test_progress_bar_defaults
FAILED tests/test_edge_cases.py::TestFunctionDefaults::test_header_color_default
FAILED tests/test_edge_cases.py::TestFunctionDefaults::test_highlight_color_default
FAILED tests/test_git_objects.py::TestCommit::test_init_invalid_commit - Attr...
FAILED tests/test_git_objects.py::TestCommit::test_get_parents - AssertionErr...
FAILED tests/test_git_objects.py::TestBranch::test_init_local_branch - Assert...
FAILED tests/test_git_objects.py::TestBranch::test_init_invalid_branch - Fail...
FAILED tests/test_git_objects.py::TestBranch::test_get_last_activity - Attrib...
FAILED tests/test_git_objects.py::TestBranch::test_to_dict - assert True is F...
FAILED tests/test_git_objects.py::TestPullRequest::test_init_valid_pr - Attri...
FAILED tests/test_git_objects.py::TestPullRequest::test_init_invalid_pr - Att...
FAILED tests/test_git_objects.py::TestPullRequest::test_is_mergeable - Assert...
FAILED tests/test_git_objects.py::TestPullRequest::test_to_dict - KeyError: '...
FAILED tests/test_git_objects.py::TestPullRequest::test_str_representation - ...
FAILED tests/test_git_objects.py::TestRepositoryIntegration::test_repository_get_commits
FAILED tests/test_git_objects.py::TestRepositoryIntegration::test_repository_get_branches
FAILED tests/test_git_objects.py::TestRepositoryIntegration::test_repository_get_commit
FAILED tests/test_git_objects.py::TestRepositoryIntegration::test_repository_get_branch
FAILED tests/test_git_objects.py::TestRepositoryIntegration::test_repository_get_branch_not_found
FAILED tests/test_github_utils.py::TestGitHubUtils::test_parse_github_url_https_with_path
FAILED tests/test_github_utils.py::TestGitHubUtils::test_parse_github_url_non_github_domain
FAILED tests/test_github_utils.py::TestGitHubUtils::test_is_public_repository_rate_limited_fallback_public
FAILED tests/test_github_utils.py::TestGitHubUtils::test_get_repository_info_success
FAILED tests/test_github_utils.py::TestGitHubUtils::test_get_repository_info_rate_limited
FAILED tests/test_github_utils.py::TestGitHubUtils::test_clone_repository_public_success
FAILED tests/test_github_utils.py::TestGitHubUtils::test_clone_repository_private_with_token
FAILED tests/test_github_utils.py::TestGitHubUtils::test_clone_repository_not_found
FAILED tests/test_github_utils.py::TestGitHubUtils::test_clone_repository_to_local_path
FAILED tests/test_github_utils.py::TestGitHubUtils::test_cleanup_temp_directories
FAILED tests/test_github_utils.py::TestGitHubUtils::test_destructor_cleanup
FAILED tests/test_github_utils.py::TestGitHubUtilsAdvanced::test_empty_repository_handling
FAILED tests/test_integration.py::TestEndToEndIntegration::test_llm_issue_generation_pipeline
FAILED tests/test_integration.py::TestEndToEndIntegration::test_sample_issue_generation_pipeline
FAILED tests/test_issue.py::TestTemplateCreation::test_create_issues_with_templates_success
FAILED tests/test_issue.py::TestTemplateCreation::test_create_issues_with_templates_creation_errors
FAILED tests/test_llm.py::TestLLMBackend::test_mock_backend_get_model_info - ...
FAILED tests/test_llm.py::TestLLMBackend::test_openai_backend_init - Attribut...
FAILED tests/test_llm.py::TestLLMBackend::test_openai_backend_init_missing_api_key
FAILED tests/test_llm.py::TestLLMBackend::test_openai_generate - ticket_maste...
FAILED tests/test_llm.py::TestLLMBackend::test_openai_generate_error - Assert...
FAILED tests/test_llm.py::TestLLMBackend::test_openai_is_available - Assertio...
FAILED tests/test_llm.py::TestLLM::test_init_with_enum_provider - ticket_mast...
FAILED tests/test_llm.py::TestLLM::test_init_with_string_provider - Assertion...
FAILED tests/test_llm.py::TestLLM::test_llm_generate_end_to_end - ticket_mast...
FAILED tests/test_llm.py::TestLLM::test_metadata - ticket_master_consolidated...
FAILED tests/test_llm.py::TestLLM::test_mock_llm_integration - ticket_master_...
FAILED tests/test_llm.py::TestLLM::test_openai_initialization - ticket_master...
FAILED tests/test_llm.py::TestLLMModelInstallation::test_install_model_backend_not_supported
FAILED tests/test_llm.py::TestLLMModelInstallation::test_install_model_ollama_success
FAILED tests/test_llm.py::TestLLMModelInstallation::test_install_model_unsupported_provider
FAILED tests/test_llm.py::TestLLMModelAvailability::test_check_model_availability_available
FAILED tests/test_llm.py::TestLLMModelAvailability::test_check_model_availability_not_available
FAILED tests/test_llm.py::TestLLMModelAvailability::test_check_model_availability_with_auto_install
FAILED tests/test_llm.py::TestLLMListModels::test_list_available_models_failure
FAILED tests/test_llm.py::TestLLMListModels::test_list_available_models_success
FAILED tests/test_llm.py::TestLLMBackendListing::test_list_available_backends
FAILED tests/test_llm.py::TestLLMBackendListing::test_list_available_backends_with_fallbacks
FAILED tests/test_llm.py::TestLLMFailureScenarios::test_generate_all_backends_fail
FAILED tests/test_llm.py::TestLLMFailureScenarios::test_generate_validation_failure
FAILED tests/test_llm.py::TestLLMFailureScenarios::test_generate_with_primary_failure_fallback_success
FAILED tests/test_llm.py::TestLLMFailureScenarios::test_generate_with_retries
FAILED tests/test_llm.py::TestLLMFailureScenarios::test_response_validation_empty_response
FAILED tests/test_llm.py::TestLLMFailureScenarios::test_response_validation_error_patterns
FAILED tests/test_llm.py::TestLLMFailureScenarios::test_response_validation_repetitive_content
FAILED tests/test_llm.py::TestOpenAIIntegration::test_openai_backend_custom_base_url
FAILED tests/test_llm.py::TestOpenAIIntegration::test_openai_backend_initialization
FAILED tests/test_llm.py::TestOpenAIIntegration::test_openai_generate_success
FAILED tests/test_llm.py::TestOpenAIIntegration::test_openai_is_available_success
FAILED tests/test_main.py::TestGenerateSampleIssues::test_generate_sample_issues_basic
FAILED tests/test_main.py::TestValidateConfigCommand::test_validate_config_command_valid_config
FAILED tests/test_main.py::TestValidateConfigCommand::test_validate_config_command_with_path
FAILED tests/test_main.py::TestAnalyzeRepository::test_analyze_repository_success
FAILED tests/test_main.py::TestGenerateIssuesWithLLM::test_generate_issues_with_llm_fallback
FAILED tests/test_main.py::TestGenerateIssuesWithLLM::test_generate_issues_with_llm_success
FAILED tests/test_main.py::TestCreateIssuesOnGitHub::test_create_issues_on_github_dry_run
FAILED tests/test_main.py::TestCreateIssuesOnGitHub::test_create_issues_on_github_failure
FAILED tests/test_main.py::TestCreateIssuesOnGitHub::test_create_issues_on_github_success
FAILED tests/test_new_classes.py::TestUserDatabase::test_cache_repository_data
FAILED tests/test_new_classes.py::TestUserDatabase::test_connect_disconnect
FAILED tests/test_new_classes.py::TestUserDatabase::test_context_manager - Ty...
FAILED tests/test_new_classes.py::TestUserDatabase::test_create_tables - Type...
FAILED tests/test_new_classes.py::TestUserDatabase::test_user_preferences - T...
FAILED tests/test_new_classes.py::TestPromptTemplate::test_get_required_variables
FAILED tests/test_new_classes.py::TestPromptTemplate::test_init_string_prompt_type
FAILED tests/test_new_classes.py::TestPromptTemplate::test_init_valid_template
FAILED tests/test_new_classes.py::TestPromptTemplate::test_provider_variations
FAILED tests/test_new_classes.py::TestPromptTemplate::test_render_basic - Typ...
FAILED tests/test_new_classes.py::TestPromptTemplate::test_render_missing_variable
FAILED tests/test_new_classes.py::TestPrompt::test_add_template - TypeError: ...
FAILED tests/test_new_classes.py::TestPrompt::test_create_builtin_templates
FAILED tests/test_new_classes.py::TestPrompt::test_get_template - TypeError: ...
FAILED tests/test_new_classes.py::TestPrompt::test_init - TypeError: Prompt._...
FAILED tests/test_new_classes.py::TestPrompt::test_list_templates - TypeError...
FAILED tests/test_new_classes.py::TestPrompt::test_render_template - TypeErro...
FAILED tests/test_new_classes.py::TestLLMBackend::test_huggingface_backend_init
FAILED tests/test_new_classes.py::TestLLMBackend::test_huggingface_generate
FAILED tests/test_new_classes.py::TestLLMBackend::test_huggingface_get_model_info
FAILED tests/test_new_classes.py::TestLLMBackend::test_huggingface_is_available
FAILED tests/test_new_classes.py::TestLLM::test_create_backend_huggingface - ...
FAILED tests/test_new_classes.py::TestLLM::test_init_huggingface_provider - t...
FAILED tests/test_new_classes.py::TestLLM::test_init_with_enum_provider - tic...
FAILED tests/test_new_classes.py::TestLLM::test_init_with_string_provider - A...
FAILED tests/test_new_classes.py::TestLLM::test_metadata - ticket_master_cons...
FAILED tests/test_new_classes.py::TestPipelineStep::test_execute_basic - Type...
FAILED tests/test_new_classes.py::TestPipelineStep::test_init - TypeError: Pr...
FAILED tests/test_new_classes.py::TestPipe::test_add_step - TypeError: Pipe._...
FAILED tests/test_new_classes.py::TestPipe::test_init - TypeError: Pipe.__ini...
FAILED tests/test_new_classes.py::TestPipe::test_validate_pipeline - TypeErro...
FAILED tests/test_new_classes.py::TestDataScraper::test_scrape_content_analysis
FAILED tests/test_new_classes.py::TestDataScraper::test_scrape_file_structure
FAILED tests/test_new_classes.py::TestDataScraper::test_scrape_repository_info
FAILED tests/test_ollama_tools.py::TestOllamaPromptProcessor::test_batch_process_prompts
FAILED tests/test_ollama_tools.py::TestOllamaPromptProcessor::test_check_model_availability
FAILED tests/test_ollama_tools.py::TestOllamaPromptProcessor::test_generate_issues_from_analysis
FAILED tests/test_ollama_tools.py::TestOllamaPromptProcessor::test_get_model_info
FAILED tests/test_ollama_tools.py::TestOllamaPromptProcessor::test_init - Mod...
FAILED tests/test_ollama_tools.py::TestOllamaPromptProcessor::test_install_model
FAILED tests/test_ollama_tools.py::TestOllamaPromptProcessor::test_parse_issues_response_json
FAILED tests/test_ollama_tools.py::TestOllamaPromptProcessor::test_parse_issues_response_text
FAILED tests/test_ollama_tools.py::TestOllamaPromptProcessor::test_process_prompt_api_error
FAILED tests/test_ollama_tools.py::TestOllamaPromptProcessor::test_process_prompt_success
FAILED tests/test_ollama_tools.py::TestOllamaPromptProcessor::test_process_prompt_with_options
FAILED tests/test_ollama_tools.py::TestOllamaPromptValidator::test_validate_prompt_template_missing_ollama_variation
FAILED tests/test_ollama_tools.py::TestOllamaPromptValidator::test_validate_prompt_template_missing_required_vars
FAILED tests/test_ollama_tools.py::TestOllamaPromptValidator::test_validate_prompt_template_too_long
FAILED tests/test_ollama_tools.py::TestOllamaPromptValidator::test_validate_prompt_template_valid
FAILED tests/test_ollama_tools.py::TestOllamaPromptValidator::test_validate_variables_missing
FAILED tests/test_ollama_tools.py::TestOllamaPromptValidator::test_validate_variables_none_values
FAILED tests/test_ollama_tools.py::TestOllamaPromptValidator::test_validate_variables_unused
FAILED tests/test_ollama_tools.py::TestOllamaPromptValidator::test_validate_variables_valid
FAILED tests/test_ollama_tools.py::TestOllamaAdvancedIntegration::test_concurrent_request_handling
FAILED tests/test_ollama_tools.py::TestOllamaAdvancedIntegration::test_connection_retry_logic
FAILED tests/test_ollama_tools.py::TestOllamaAdvancedIntegration::test_custom_generation_parameters
FAILED tests/test_ollama_tools.py::TestOllamaAdvancedIntegration::test_memory_optimization_large_prompts
FAILED tests/test_ollama_tools.py::TestOllamaAdvancedIntegration::test_model_info_detailed
FAILED tests/test_ollama_tools.py::TestOllamaAdvancedIntegration::test_model_installation_failure_scenarios
FAILED tests/test_ollama_tools.py::TestOllamaAdvancedIntegration::test_model_installation_with_progress
FAILED tests/test_ollama_tools.py::TestOllamaAdvancedIntegration::test_model_switching
FAILED tests/test_ollama_tools.py::TestOllamaAdvancedIntegration::test_response_streaming_handling
FAILED tests/test_ollama_tools.py::TestOllamaErrorRecovery::test_insufficient_memory_handling
FAILED tests/test_ollama_tools.py::TestOllamaErrorRecovery::test_invalid_prompt_handling
FAILED tests/test_ollama_tools.py::TestOllamaErrorRecovery::test_model_loading_timeout_handling
FAILED tests/test_performance.py::TestLargeRepositoryPerformance::test_bulk_data_processing_performance
FAILED tests/test_performance.py::TestLargeRepositoryPerformance::test_large_commit_history_performance
FAILED tests/test_performance.py::TestLargeRepositoryPerformance::test_large_file_count_performance
FAILED tests/test_performance.py::TestBulkOperationsPerformance::test_bulk_issue_creation_performance
FAILED tests/test_pipe.py::TestPipelineStep::test_execute_basic - TypeError: ...
FAILED tests/test_pipe.py::TestPipelineStep::test_execute_with_llm_error - Ty...
FAILED tests/test_pipe.py::TestPipelineStep::test_execute_with_validation_exception
FAILED tests/test_pipe.py::TestPipelineStep::test_execute_with_validation_failure
FAILED tests/test_pipe.py::TestPipelineStep::test_execute_with_validation_success
FAILED tests/test_pipe.py::TestPipelineStep::test_init - TypeError: PromptTem...
FAILED tests/test_pipe.py::TestPipelineStep::test_init_with_custom_stage - Ty...
FAILED tests/test_pipe.py::TestPipelineStep::test_init_with_validation_function
FAILED tests/test_pipe.py::TestPipelineStep::test_str_method - TypeError: Pro...
FAILED tests/test_pipe.py::TestPipe::test_add_step - TypeError: Pipe.__init__...
FAILED tests/test_pipe.py::TestPipe::test_add_step_duplicate_name - TypeError...
FAILED tests/test_pipe.py::TestPipe::test_add_step_max_steps_exceeded - TypeE...
FAILED tests/test_pipe.py::TestPipe::test_add_step_with_validation - TypeErro...
FAILED tests/test_pipe.py::TestPipe::test_clear_steps - TypeError: Pipe.__ini...
FAILED tests/test_pipe.py::TestPipe::test_execute_empty_pipeline - TypeError:...
FAILED tests/test_pipe.py::TestPipe::test_execute_multiple_steps - TypeError:...
FAILED tests/test_pipe.py::TestPipe::test_execute_single_step - TypeError: Pi...
FAILED tests/test_pipe.py::TestPipe::test_execute_with_step_failure - TypeErr...
FAILED tests/test_pipe.py::TestPipe::test_get_step_names - TypeError: Pipe.__...
FAILED tests/test_pipe.py::TestPipe::test_get_steps_by_stage - TypeError: Pip...
FAILED tests/test_pipe.py::TestPipe::test_init - TypeError: Pipe.__init__() t...
FAILED tests/test_pipe.py::TestPipe::test_init_with_optional_params - TypeErr...
FAILED tests/test_pipe.py::TestPipe::test_len_method - TypeError: Pipe.__init...
FAILED tests/test_pipe.py::TestPipe::test_remove_step - TypeError: Pipe.__ini...
FAILED tests/test_pipe.py::TestPipe::test_remove_step_nonexistent - TypeError...
FAILED tests/test_pipe.py::TestPipe::test_repr_method - TypeError: Pipe.__ini...
FAILED tests/test_pipe.py::TestPipe::test_str_method - TypeError: Pipe.__init...
FAILED tests/test_pipe.py::TestPipe::test_to_dict - TypeError: Pipe.__init__(...
FAILED tests/test_pipe.py::TestPipe::test_validate_pipeline - TypeError: Pipe...
FAILED tests/test_pipe.py::TestPipe::test_validate_pipeline_missing_input_stage
FAILED tests/test_pipe.py::TestPipe::test_validate_pipeline_missing_output_stage
FAILED tests/test_pipe.py::TestPipe::test_validate_pipeline_with_steps - Type...
FAILED tests/test_pipe.py::TestPipeStage::test_pipe_stage_values - AttributeE...
FAILED tests/test_prompt.py::TestPromptTemplate::test_get_required_variables
FAILED tests/test_prompt.py::TestPromptTemplate::test_init_string_prompt_type
FAILED tests/test_prompt.py::TestPromptTemplate::test_init_valid_template - T...
FAILED tests/test_prompt.py::TestPromptTemplate::test_provider_variations - T...
FAILED tests/test_prompt.py::TestPromptTemplate::test_render_basic - TypeErro...
FAILED tests/test_prompt.py::TestPromptTemplate::test_render_missing_variable
FAILED tests/test_prompt.py::TestPrompt::test_add_template - TypeError: Promp...
FAILED tests/test_prompt.py::TestPrompt::test_create_builtin_templates - Type...
FAILED tests/test_prompt.py::TestPrompt::test_get_template - TypeError: Promp...
FAILED tests/test_prompt.py::TestPrompt::test_init - TypeError: Prompt.__init...
FAILED tests/test_prompt.py::TestPrompt::test_list_templates - TypeError: Pro...
FAILED tests/test_prompt.py::TestPrompt::test_render_template - TypeError: Pr...
FAILED tests/test_pull_request.py::TestPullRequest::test_get_branch_info - At...
FAILED tests/test_pull_request.py::TestPullRequest::test_get_changed_files - ...
FAILED tests/test_pull_request.py::TestPullRequest::test_get_changed_files_error
FAILED tests/test_pull_request.py::TestPullRequest::test_get_comments - Attri...
FAILED tests/test_pull_request.py::TestPullRequest::test_get_comments_error
FAILED tests/test_pull_request.py::TestPullRequest::test_get_commits_error - ...
FAILED tests/test_pull_request.py::TestPullRequest::test_get_reviews_error - ...
FAILED tests/test_pull_request.py::TestPullRequest::test_is_approved_with_approvals
FAILED tests/test_repository.py::TestRepository::test_get_repository_info - A...
FAILED tests/test_repository.py::TestRepository::test_repr_representation - a...
======================= 284 failed, 284 passed in 17.41s =======================
```