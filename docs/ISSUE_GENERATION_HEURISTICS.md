# Issue Generation Heuristics - Draft

This document outlines various heuristics and algorithms for automatically determining what repository conditions should trigger the creation of GitHub issues in the Ticket-Master system.

## Overview

The goal is to create intelligent, data-driven heuristics that can automatically identify actionable issues within a codebase. Each heuristic should be configurable with thresholds and scoring mechanisms to ensure relevance and prevent noise.

## Core Heuristic Categories

### 1. Code Quality Grading System (0-100 Scale)

#### 1.1 Overall Code Quality Score
- **Weight Distribution:**
  - Code complexity: 25%
  - Documentation coverage: 20%
  - Test coverage: 20%
  - Code style consistency: 15%
  - File organization: 10%
  - Dependency health: 10%

#### 1.2 Quality Metrics
- **Excellent (90-100):** Well-documented, tested, and maintainable code
- **Good (70-89):** Minor improvements needed
- **Fair (50-69):** Moderate issues requiring attention
- **Poor (30-49):** Significant problems need addressing
- **Critical (0-29):** Major refactoring or fixes required

#### 1.3 Issue Generation Triggers
- Score < 70: Generate "Code Quality Improvement" issue
- Score < 50: Generate "Critical Code Quality Issues" issue with high priority
- Individual component score < 40: Generate component-specific issues

### 2. TODO Comment Detection

#### 2.1 TODO Pattern Matching
```regex
// TODO:?\s*(.*)
# TODO:?\s*(.*)
<!-- TODO:?\s*(.*?) -->
/\* TODO:?\s*(.*?)\*/
```

#### 2.2 Additional Comment Patterns
- `FIXME`, `XXX`, `HACK`, `BUG`
- `NOTE:`, `WARNING:`, `IMPORTANT:`
- Custom markers: `@todo`, `@fix`, `@refactor`

#### 2.3 Scoring System
- **Critical TODO (10 points):** Contains "urgent", "critical", "security", "bug"
- **High Priority TODO (7 points):** Contains "performance", "refactor", "cleanup"
- **Medium Priority TODO (5 points):** Contains "improve", "optimize", "enhance"
- **Low Priority TODO (3 points):** General improvements, documentation

#### 2.4 Issue Generation Rules
- 5+ TODOs in a single file: Generate file-specific cleanup issue
- 20+ TODOs across project: Generate project-wide cleanup issue
- Critical TODOs (any count): Generate immediate action issue
- TODOs older than 6 months (via git blame): Generate stale TODO cleanup issue

### 3. Code Smell and Clarity Detection

#### 3.1 Structural Code Smells
- **Long Methods:** Methods > 50 lines (configurable)
- **Large Classes:** Classes > 500 lines (configurable)
- **Long Parameter Lists:** Methods with > 5 parameters
- **Duplicate Code:** Similar code blocks > 6 lines
- **Complex Conditionals:** Nested if/else > 4 levels deep

#### 3.2 Naming Convention Issues
- **Inconsistent Naming:** Mixed camelCase/snake_case within same file
- **Unclear Variable Names:** Single letter variables (except loops)
- **Abbreviated Names:** Variables like `usr`, `tmp`, `val` without context
- **Hungarian Notation:** Legacy prefixes like `str`, `int`, `bool`

#### 3.3 Architecture Smells
- **God Classes:** Classes with > 10 responsibilities
- **Tight Coupling:** High interdependency between modules
- **Feature Envy:** Methods heavily using other classes' data
- **Inappropriate Intimacy:** Classes accessing each other's internals

#### 3.4 Issue Generation Triggers
- 3+ code smells in one file: Generate refactoring issue
- Architecture smells detected: Generate design review issue
- Naming inconsistencies > 20% of identifiers: Generate naming convention issue

### 4. File Size and Complexity Analysis

#### 4.1 File Size Metrics
- **Small:** < 100 lines
- **Medium:** 100-300 lines
- **Large:** 300-1000 lines
- **Huge:** > 1000 lines

#### 4.2 Cyclomatic Complexity
- **Simple:** 1-10 complexity score
- **Moderate:** 11-20 complexity score
- **Complex:** 21-50 complexity score
- **Very Complex:** > 50 complexity score

#### 4.3 Issue Triggers
- Files > 1500 lines: Generate "File Size Reduction" issue
- Functions with complexity > 30: Generate "Function Complexity" issue
- Average file complexity > 25: Generate "Codebase Complexity" issue

### 5. Commit Pattern Analysis

#### 5.1 Commit Message Quality
- **Good Patterns:** Follows conventional commits, descriptive messages
- **Warning Patterns:** Generic messages like "fix", "update", "wip"
- **Bad Patterns:** Empty messages, single words, profanity

#### 5.2 File Hotspot Analysis
- **Hot Files:** Files modified in > 30% of recent commits
- **Abandoned Files:** Files not modified in > 6 months
- **Churning Files:** Files with high add/delete ratio

#### 5.3 Issue Generation
- Hot files detected: Generate "Code Hotspot Review" issue
- Poor commit message ratio > 40%: Generate "Commit Quality" issue
- Large commits (> 500 lines): Generate "Commit Size Review" issue

### 6. Documentation Coverage Analysis

#### 6.1 Documentation Types
- **API Documentation:** Function/method docstrings
- **README Files:** Project overview, setup, usage
- **Code Comments:** Inline explanations
- **Architecture Documentation:** Design decisions, patterns

#### 6.2 Coverage Metrics
- **Function Documentation:** % of public functions with docstrings
- **Class Documentation:** % of classes with descriptions
- **Module Documentation:** % of modules with headers
- **README Quality:** Presence of installation, usage, examples

#### 6.3 Issue Triggers
- Function documentation < 60%: Generate "API Documentation" issue
- Missing README sections: Generate "Documentation Completeness" issue
- No architecture docs + large codebase: Generate "Architecture Documentation" issue

### 7. Test Coverage Analysis

#### 7.1 Coverage Metrics
- **Line Coverage:** % of code lines executed by tests
- **Branch Coverage:** % of code branches tested
- **Function Coverage:** % of functions with tests
- **Integration Coverage:** % of component interactions tested

#### 7.2 Quality Indicators
- **Test File Ratio:** Test files to source files ratio
- **Test Naming:** Descriptive test names vs generic names
- **Test Organization:** Proper test structure and grouping

#### 7.3 Issue Generation
- Line coverage < 70%: Generate "Test Coverage Improvement" issue
- No tests for new files: Generate "Test Missing for New Code" issue
- Test files older than source files: Generate "Test Maintenance" issue

### 8. Security Vulnerability Detection

#### 8.1 Pattern-Based Detection
- **Hardcoded Secrets:** API keys, passwords, tokens in code
- **SQL Injection Risks:** String concatenation in queries
- **XSS Vulnerabilities:** Unescaped user input in templates
- **Path Traversal:** Unsanitized file path operations

#### 8.2 Dependency Vulnerabilities
- **Outdated Dependencies:** Libraries with known CVEs
- **Unmaintained Dependencies:** Libraries not updated in > 2 years
- **License Issues:** Dependencies with incompatible licenses

#### 8.3 Issue Generation
- Any hardcoded secrets: Generate "Security: Remove Secrets" issue (HIGH PRIORITY)
- Vulnerable dependencies: Generate "Security: Update Dependencies" issue
- Multiple security patterns: Generate "Security Audit Required" issue

### 9. Dependency Management

#### 9.1 Dependency Health Metrics
- **Update Frequency:** How often dependencies are updated
- **Version Pinning:** Use of exact vs range versioning
- **Dependency Count:** Total number of dependencies
- **Circular Dependencies:** Dependencies that create cycles

#### 9.2 Package Manager Analysis
- **Python:** requirements.txt, setup.py, Pipfile analysis
- **Node.js:** package.json, yarn.lock analysis
- **Java:** pom.xml, build.gradle analysis
- **Go:** go.mod analysis

#### 9.3 Issue Triggers
- > 100 dependencies: Generate "Dependency Audit" issue
- Major version updates available: Generate "Dependency Updates" issue
- Circular dependencies detected: Generate "Dependency Restructure" issue

### 10. Performance Bottleneck Identification

#### 10.1 Code Pattern Analysis
- **Inefficient Loops:** Nested loops with high complexity
- **Resource Leaks:** Unclosed files, connections, streams
- **Memory Issues:** Large object creation in loops
- **Database Issues:** N+1 queries, missing indexes

#### 10.2 File Size Performance
- **Large Config Files:** JSON/YAML files > 1MB
- **Binary Files:** Committed binary files > 10MB
- **Log Files:** Committed log files

#### 10.3 Issue Generation
- Performance anti-patterns detected: Generate "Performance Review" issue
- Large files in repo: Generate "Repository Cleanup" issue
- Resource leak patterns: Generate "Resource Management" issue

## Heuristic Configuration

### Threshold Configuration
```yaml
heuristics:
  code_quality:
    minimum_score: 70
    critical_threshold: 50
  
  todo_detection:
    max_todos_per_file: 5
    max_project_todos: 20
    critical_keywords: ["urgent", "critical", "security", "bug"]
  
  file_complexity:
    max_file_lines: 1000
    max_function_complexity: 30
    max_class_lines: 500
  
  commit_analysis:
    hotspot_threshold: 0.3  # 30% of commits
    large_commit_lines: 500
  
  documentation:
    min_function_coverage: 0.6  # 60%
    required_readme_sections: ["installation", "usage", "examples"]
  
  testing:
    min_line_coverage: 0.7  # 70%
    test_to_source_ratio: 0.8
  
  security:
    secret_patterns: ["api_key", "password", "token", "secret"]
    max_dependency_age_months: 24
  
  performance:
    max_nested_loops: 3
    max_config_file_size: 1048576  # 1MB
```

### Scoring Weights
```yaml
scoring:
  code_quality_weights:
    complexity: 0.25
    documentation: 0.20
    testing: 0.20
    style: 0.15
    organization: 0.10
    dependencies: 0.10
  
  issue_priority_multipliers:
    security: 3.0
    critical_bugs: 2.5
    performance: 2.0
    maintenance: 1.5
    documentation: 1.0
    style: 0.8
```

## Implementation Strategy

### Phase 1: Core Heuristics
1. Implement TODO comment detection
2. Basic code quality scoring
3. File size and complexity analysis
4. Simple documentation coverage

### Phase 2: Advanced Analysis
1. Code smell detection algorithms
2. Commit pattern analysis
3. Security vulnerability scanning
4. Test coverage integration

### Phase 3: Machine Learning Enhancement
1. Pattern recognition for code smells
2. Historical analysis for prediction
3. Custom heuristic learning
4. False positive reduction

### Phase 4: Integration and Optimization
1. Performance optimization
2. Configurable thresholds
3. Custom rule engine
4. Reporting and analytics

## Expected Output Format

Each heuristic should generate issues in this format:

```python
Issue(
    title="[HEURISTIC_TYPE] Descriptive Title",
    description="""
    ## Issue Category: {category}
    
    **Detected by:** {heuristic_name}
    **Severity:** {severity_level}
    **Confidence:** {confidence_score}%
    
    ## Problem Description
    {detailed_description}
    
    ## Affected Files/Areas
    {file_list_or_areas}
    
    ## Recommended Actions
    {action_items}
    
    ## Technical Details
    {metrics_and_specifics}
    
    ---
    *This issue was automatically generated by Ticket-Master using {heuristic_name} heuristic.*
    """,
    labels=["automated", category, severity],
    assignees=configuration_based_assignees
)
```

## Future Enhancements

1. **AI/LLM Integration:** Use language models for contextual code analysis
2. **Team-Specific Patterns:** Learn from team's historical issue patterns
3. **Cross-Repository Analysis:** Compare against similar projects
4. **Temporal Analysis:** Track how issues evolve over time
5. **Custom Heuristics:** Allow teams to define their own rules
6. **Integration APIs:** Connect with other development tools
7. **Predictive Analysis:** Predict future issues based on trends

---

*This document is a living specification that will be updated as heuristics are implemented and refined based on real-world usage and feedback.*