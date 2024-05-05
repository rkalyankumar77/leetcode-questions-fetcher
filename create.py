#!/usr/bin/env python3


import os
import argparse
import requests
import html2text


class LeetScrapeException(Exception):
    pass



headers = {
# To get the headers check the README.md file
}

def fetch_leetcode_question_content(question_slug) -> str:
    graphql_endpoint = "https://leetcode.com/graphql/"

    data = {
        "query": """
    query questionContent($titleSlug: String!) { 
    question(titleSlug: $titleSlug) { 
        content 
        mysqlSchemas 
        dataSchemas 
    } 
    }
    """,
        "variables": {"titleSlug": question_slug},
        "operationName": "questionContent",
    }

    headers["Referer"] = f"https://leetcode.com/problems/{question_slug}/description/"
    response = requests.post(graphql_endpoint, headers=headers, json=data)

    if response.status_code == 200:
        response_data = response.json()
        content_raw = response_data["data"]["question"]["content"]
        h = html2text.HTML2Text()
        h.ignore_links = True  # Optionally ignore links
        markdown_text = h.handle(content_raw)
        return markdown_text
    else:
        print("Error:", response.status_code, response.text)
        raise (LeetScrapeException(f"Error: {response.status_code} - {response.txt}"))


def fetch_problem_code(title_slug, prog_lang_choice="Python3"):
    graphql_endpoint = "https://leetcode.com/graphql/"

    data = {
        "query": """
            query questionEditorData($titleSlug: String!) {
            question(titleSlug: $titleSlug) {
                questionId
                questionFrontendId
                codeSnippets {
                lang
                langSlug
                code
                }
                envInfo
                enableRunCode
                hasFrontendPreview
                frontendPreviews
            }
            } """,
        "variables": {"titleSlug": title_slug},
        "operationName": "questionEditorData",
    }

    headers["Referer"] = f"https://leetcode.com/problems/{title_slug}/description/"
    response = requests.post(graphql_endpoint, headers=headers, json=data)

    if response.status_code == 200:
        response_data = response.json()
        # Extract the code snippet you need (modify based on structure)
        if (
            "data" in response_data
            and "question" in response_data["data"]
            and "codeSnippets" in response_data["data"]["question"]
        ):
            code_snippets = response_data["data"]["question"]["codeSnippets"]
            # Assuming you want the first code snippet:
            if code_snippets:
                for code in code_snippets:
                    if code["lang"] == prog_lang_choice:
                        return code["code"]
            else:
                return "No code snippets found"
        else:
            return "Error extracting code"
    else:
        return f"Error: HTTP {response.status_code} - {response.text}"


def create_project_structure(leetcode_url, coding_language):
    """Creates a standardized project skeleton"""
    
    problem_slug = leetcode_url[len("https://") :].split("/")[2]

    file_name = ""
    if coding_language == "Python" or coding_language == "Python3":
        file_name = "solution.py"
    else:
        file_name = "solution"
        if coding_language == "Java":
            file_name = file_name.capitalize() + ".java"
        elif coding_language == "C++":
            file_name += ".cpp"
        elif coding_language == "C":
            file_name += ".c"
        elif coding_language == "JavaScript":
            file_name += ".js"
        elif coding_language == "TypeScript":
            file_name += ".ts"
        elif coding_language == "C#":
            file_name = file_name.capitalize + ".cs"
        elif coding_language == "PHP":
            file_name += ".php"
        elif coding_language == "Swift":
            file_name = file_name.capitalize() + ".swift"
        elif coding_language == "Kotlin":
            file_name = file_name.capitalize() + ".kt"
        elif coding_language == "Dart":
            file_name += ".dart"
        elif coding_language == "Go":
            file_name += ".go"
        elif coding_language == "Ruby":
            file_name += ".rb"
        elif coding_language == "Scala":
            file_name = file_name.capitalize + ".scala"
        elif coding_language == "Rust":
            file_name += ".rs"
        elif coding_language == "Racket":
            file_name += ".rkt"
        elif coding_language == "Erlang":
            file_name += ".erl"
        elif coding_language == "Elixir":
            file_name += ".exs"
        else:
            print("Coding language isn't supported.")
            exit(-1)


    question_content = fetch_leetcode_question_content(problem_slug)
    problem_content = fetch_problem_code(problem_slug, coding_language)

    base_dir = "./Sources/"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    problem_dir = os.path.join(base_dir, problem_slug)
    os.makedirs(problem_dir)



    solution_path = os.path.join(problem_dir, file_name)
    readme_path = os.path.join(problem_dir, "README.md")
    with open(solution_path, "w") as f:
        if coding_language == "Python3":
            f.write("#!/usr/bin/env python3\n")
            f.write("\n")
            f.write("from typing import List\n")
            f.write("from collections import defaultdict, deque\n")
            f.write("\n\n")
            f.write(f"# {leetcode_url} \n\n")
            f.write(problem_content + "\n        pass")
            f.write("\n\n")
            f.write("def main():\n    pass\n\n")
            f.write("if __name__ == '__main__':\n    main()")
        else:
            f.write(problem_content)
    with open(readme_path, "w") as f:
        f.write("# Problem Description\n")
        f.write(question_content)

    # Update the main README.md
    update_main_read_md(problem_slug, leetcode_url)


def update_main_read_md(problem_name, leetcode_url):
    # Update the main README.md
    main_readme_path = os.path.join("./", "README.md")
    problem_link = (
        f"| [{problem_name}](Sources/{problem_name}/README.md) | {leetcode_url} |\n"
    )

    with open(main_readme_path, "a") as f:  # Use 'a' for appending
        f.write(problem_link)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create solution.py and README.md file for a given leetcode problem"
    )
    parser.add_argument("leetcode_url", help="<leetcode problem url>")
    parser.add_argument(
        "--coding_language",
        help="Programming language for the solution",
        default="Python3",  # Set the default value here
    )

    args = parser.parse_args()

    create_project_structure(args.leetcode_url, args.coding_language)
