import pandas as pd
import json
import argparse


# 示例原始数据格式可能类似：
# df = pd.DataFrame({
#     'url': ['x1', 'x1', 'x1', 'x2'],
#     'name': ['n1', 'n1', 'n1', 'n2'],
#     'os': ['win', 'win', 'linux', 'mac'],
#     'arch': ['amd64', 'amd64', 'arm', 'arm64'],
#     'procedure': ['p1', 'p1', 'p2', 'p3'],
#     'question': ['q1', 'q2', 'q3', 'q4'],
#     'answer': ['a1', 'a2', 'a3', 'a4']
# })


def main():
    # 设置命令行参数
    parser = argparse.ArgumentParser(description="Convert CSV to deployment JSON")
    parser.add_argument("--input", required=True, help="Input CSV file path")
    args = parser.parse_args()

    # 读取CSV文件
    df = pd.read_csv(args.input)
    df.fillna("", inplace=True)

    # 按url和name分组聚合
    grouped = df.groupby(["url", "name"])

    result = []
    for (url, name), group in grouped:
        # 提取部署配置（去重）
        deployments = group[["os", "arch", "procedure"]].drop_duplicates()

        # 提取QA对（去重）
        qas = group[["question", "answer"]].drop_duplicates()

        # 构建条目
        entry = {
            "url": url,
            "name": name,
            "deployment": deployments.to_dict("records"),
            "qa": qas.to_dict("records"),
        }
        result.append(entry)

    # 生成带缩进的JSON
    json_output = json.dumps(result, indent=2, ensure_ascii=False)

    # 保存到文件
    with open("deployments.json", "w") as f:
        f.write(json_output)


if __name__ == "__main__":
    main()
