#!/usr/bin/env python3
"""
Test Pattern Analyzer

Discovers and analyzes test patterns in codebases.
Used for automatic test context documentation.

Usage:
    from test_pattern_analyzer import TestPatternAnalyzer

    analyzer = TestPatternAnalyzer()
    patterns = analyzer.analyze_test_file("tests/test_auth.py")
"""

import re
import ast
from pathlib import Path
from typing import Dict, List, Set, Optional
from collections import defaultdict


class TestPatternAnalyzer:
    """Analyzes test files to discover patterns"""

    def __init__(self):
        """Initialize analyzer"""
        self.framework_patterns = {
            'pytest': ['def test_', '@pytest.', 'pytest.fixture', 'assert '],
            'unittest': ['class.*TestCase', 'def test_', 'self.assert', 'unittest.'],
            'jest': ['describe(', 'it(', 'test(', 'expect('],
            'mocha': ['describe(', 'it(', 'before(', 'after('],
            'vitest': ['describe(', 'it(', 'test(', 'expect(', 'vi.'],
        }

    def detect_test_framework(self, file_path: Path) -> Optional[str]:
        """Detect which test framework is being used"""
        try:
            content = file_path.read_text()

            scores = defaultdict(int)
            for framework, patterns in self.framework_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, content):
                        scores[framework] += 1

            if not scores:
                return None

            # Return framework with highest score
            return max(scores, key=scores.get)
        except Exception:
            return None

    def analyze_python_test(self, file_path: Path) -> Dict:
        """Analyze Python test file for patterns"""
        try:
            content = file_path.read_text()
            tree = ast.parse(content)
        except Exception as e:
            return {"error": str(e)}

        patterns = {
            "framework": self.detect_test_framework(file_path),
            "test_functions": [],
            "fixtures": [],
            "mocks": [],
            "assertions": [],
            "setup_teardown": {},
            "imports": [],
            "patterns_found": set()
        }

        # Analyze imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    patterns["imports"].append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    patterns["imports"].append(node.module)

        # Analyze test functions and classes
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Test functions
                if node.name.startswith('test_'):
                    patterns["test_functions"].append({
                        "name": node.name,
                        "docstring": ast.get_docstring(node),
                        "line": node.lineno
                    })

                # Fixtures (pytest)
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name) and decorator.id == 'fixture':
                        patterns["fixtures"].append(node.name)
                    elif isinstance(decorator, ast.Attribute) and decorator.attr == 'fixture':
                        patterns["fixtures"].append(node.name)

                # Setup/Teardown (unittest)
                if node.name in ['setUp', 'tearDown', 'setUpClass', 'tearDownClass']:
                    patterns["setup_teardown"][node.name] = node.lineno

            # Test classes
            elif isinstance(node, ast.ClassDef):
                if 'TestCase' in [base.id for base in node.bases if isinstance(base, ast.Name)]:
                    patterns["patterns_found"].add("unittest.TestCase pattern")

        # Detect mocking patterns
        mock_indicators = ['Mock(', 'MagicMock(', 'patch(', '@patch', 'mock.']
        for indicator in mock_indicators:
            if indicator in content:
                patterns["mocks"].append(indicator)
                patterns["patterns_found"].add(f"Mocking with {indicator}")

        # Detect assertion styles
        assertion_patterns = {
            'assert ': 'Direct assertions',
            'self.assertEqual': 'unittest assertEqual',
            'self.assertTrue': 'unittest assertTrue',
            'self.assertRaises': 'Exception testing',
            'pytest.raises': 'pytest exception testing',
            '@pytest.mark.parametrize': 'Parametrized tests',
        }

        for pattern, description in assertion_patterns.items():
            if pattern in content:
                patterns["assertions"].append(pattern)
                patterns["patterns_found"].add(description)

        # Convert set to list for JSON serialization
        patterns["patterns_found"] = list(patterns["patterns_found"])

        return patterns

    def analyze_javascript_test(self, file_path: Path) -> Dict:
        """Analyze JavaScript/TypeScript test file for patterns"""
        try:
            content = file_path.read_text()
        except Exception as e:
            return {"error": str(e)}

        patterns = {
            "framework": self.detect_test_framework(file_path),
            "test_suites": [],
            "test_cases": [],
            "hooks": [],
            "mocks": [],
            "assertions": [],
            "patterns_found": set()
        }

        # Find describe blocks (test suites)
        describe_pattern = r"describe\(['\"](.+?)['\"]"
        for match in re.finditer(describe_pattern, content):
            patterns["test_suites"].append(match.group(1))

        # Find it/test blocks (test cases)
        test_pattern = r"(?:it|test)\(['\"](.+?)['\"]"
        for match in re.finditer(test_pattern, content):
            patterns["test_cases"].append(match.group(1))

        # Find hooks
        hook_patterns = ['beforeEach', 'afterEach', 'beforeAll', 'afterAll', 'before', 'after']
        for hook in hook_patterns:
            if hook + '(' in content:
                patterns["hooks"].append(hook)

        # Detect mocking patterns
        mock_indicators = {
            'jest.fn()': 'Jest mock functions',
            'jest.mock(': 'Jest module mocking',
            'jest.spyOn': 'Jest spies',
            'vi.fn()': 'Vitest mock functions',
            'vi.mock(': 'Vitest module mocking',
            'sinon.': 'Sinon mocking',
            'cy.stub': 'Cypress stubbing',
        }

        for indicator, description in mock_indicators.items():
            if indicator in content:
                patterns["mocks"].append(indicator)
                patterns["patterns_found"].add(description)

        # Detect assertion styles
        assertion_patterns = {
            'expect(': 'Expect assertions',
            '.toBe(': 'toBe matcher',
            '.toEqual(': 'toEqual matcher',
            '.toHaveBeenCalled': 'Mock verification',
            'assert.': 'Assert library',
            'should.': 'Should.js assertions',
        }

        for pattern, description in assertion_patterns.items():
            if pattern in content:
                patterns["assertions"].append(pattern)
                patterns["patterns_found"].add(description)

        # Async patterns
        if 'async ' in content or 'await ' in content:
            patterns["patterns_found"].add("Async/await testing")

        # Convert set to list
        patterns["patterns_found"] = list(patterns["patterns_found"])

        return patterns

    def analyze_test_file(self, file_path: Path) -> Dict:
        """Analyze any test file and return discovered patterns"""
        file_path = Path(file_path)

        if not file_path.exists():
            return {"error": "File not found"}

        # Determine language
        suffix = file_path.suffix

        if suffix == '.py':
            return self.analyze_python_test(file_path)
        elif suffix in ['.js', '.ts', '.jsx', '.tsx']:
            return self.analyze_javascript_test(file_path)
        else:
            return {"error": f"Unsupported file type: {suffix}"}

    def analyze_test_directory(self, dir_path: Path) -> Dict:
        """Analyze all test files in a directory"""
        dir_path = Path(dir_path)

        if not dir_path.exists() or not dir_path.is_dir():
            return {"error": "Directory not found"}

        results = {
            "directory": str(dir_path),
            "files_analyzed": 0,
            "frameworks_detected": set(),
            "common_patterns": defaultdict(int),
            "test_count": 0,
            "files": {}
        }

        # Find test files
        test_patterns = ['test_*.py', '*_test.py', '*.test.js', '*.test.ts', '*.spec.js', '*.spec.ts']
        test_files = []

        for pattern in test_patterns:
            test_files.extend(dir_path.glob(pattern))

        # Analyze each file
        for file_path in test_files:
            analysis = self.analyze_test_file(file_path)

            if "error" in analysis:
                continue

            results["files"][str(file_path.relative_to(dir_path))] = analysis
            results["files_analyzed"] += 1

            # Aggregate data
            if analysis.get("framework"):
                results["frameworks_detected"].add(analysis["framework"])

            for pattern in analysis.get("patterns_found", []):
                results["common_patterns"][pattern] += 1

            results["test_count"] += len(analysis.get("test_functions", [])) + len(analysis.get("test_cases", []))

        # Convert sets to lists for serialization
        results["frameworks_detected"] = list(results["frameworks_detected"])
        results["common_patterns"] = dict(results["common_patterns"])

        return results

    def generate_pattern_summary(self, analysis: Dict) -> str:
        """Generate human-readable summary of patterns"""
        if "error" in analysis:
            return f"Error: {analysis['error']}"

        if "directory" in analysis:
            # Directory analysis
            summary_parts = [
                f"📊 Test Directory Analysis: {analysis['directory']}",
                f"Files analyzed: {analysis['files_analyzed']}",
                f"Total tests: {analysis['test_count']}",
                ""
            ]

            if analysis["frameworks_detected"]:
                summary_parts.append(f"Frameworks: {', '.join(analysis['frameworks_detected'])}")

            if analysis["common_patterns"]:
                summary_parts.append("\nCommon Patterns:")
                for pattern, count in sorted(analysis["common_patterns"].items(), key=lambda x: -x[1]):
                    summary_parts.append(f"  • {pattern} ({count} files)")

            return "\n".join(summary_parts)
        else:
            # Single file analysis
            summary_parts = [
                f"🧪 Test Pattern Analysis",
                f"Framework: {analysis.get('framework', 'Unknown')}",
                ""
            ]

            if analysis.get("test_functions"):
                summary_parts.append(f"Test functions: {len(analysis['test_functions'])}")

            if analysis.get("test_cases"):
                summary_parts.append(f"Test cases: {len(analysis['test_cases'])}")

            if analysis.get("patterns_found"):
                summary_parts.append("\nPatterns:")
                for pattern in analysis["patterns_found"]:
                    summary_parts.append(f"  • {pattern}")

            if analysis.get("fixtures"):
                summary_parts.append(f"\nFixtures: {', '.join(analysis['fixtures'])}")

            if analysis.get("hooks"):
                summary_parts.append(f"\nHooks: {', '.join(analysis['hooks'])}")

            return "\n".join(summary_parts)


def main():
    """CLI for test pattern analyzer"""
    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: python test_pattern_analyzer.py <file_or_directory> [--json]")
        sys.exit(1)

    path = Path(sys.argv[1])
    output_json = "--json" in sys.argv

    analyzer = TestPatternAnalyzer()

    if path.is_file():
        result = analyzer.analyze_test_file(path)
    elif path.is_dir():
        result = analyzer.analyze_test_directory(path)
    else:
        print(f"Error: {path} not found")
        sys.exit(1)

    if output_json:
        print(json.dumps(result, indent=2))
    else:
        print(analyzer.generate_pattern_summary(result))


if __name__ == "__main__":
    main()
