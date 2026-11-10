import argparse
import sys
import os

def parse_args():
    parser = argparse.ArgumentParser(description="Визуализатор графов (Вариант 16)")
    
    parser.add_argument("--package", type=str, required=True, help="Имя анализируемого пакета")
    parser.add_argument("--repo", type=str, required=True, help="URL репозитория или путь к тестовому файлу")
    parser.add_argument("--test-mode", action="store_true", help="Режим тестирования")
    parser.add_argument("--depth", type=int, required=True, help="Максимальная глубина анализа")
    parser.add_argument("--output", type=str, default="graph.dot", help="Имя файла для Graphviz")
    
    return parser.parse_args()

def load_test_repo(file_path):
    if not os.path.exists(file_path):
        print(f"Ошибка: Файл репозитория не найден: {file_path}")
        sys.exit(1)
        
    dependencies = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(" depends_on ")
                if len(parts) != 2:
                    continue
                pkg = parts[0].strip()
                deps_str = parts[1].strip()
                deps = [d.strip() for d in deps_str.split(",") if d.strip()]
                dependencies[pkg] = deps
    except Exception as e:
        print(f"Ошибка чтения файла: {e}")
        sys.exit(1)
        
    return dependencies

def build_graph_dfs(node, data, max_depth, current_depth=0, visited=None):
    if visited is None:
        visited = set()
        
    if current_depth > max_depth or node in visited:
        return {}
        
    visited.add(node)
    graph = {node: []}
    
    if node in data:
        for dep in data[node]:
            graph[node].append(dep)
            sub_graph = build_graph_dfs(dep, data, max_depth, current_depth + 1, visited)
            for k, v in sub_graph.items():
                if k in graph:
                    graph[k].extend(v)
                else:
                    graph[k] = v
                    
    return graph

def get_load_order(graph, start_package):
    visited = set()
    order = []
    
    def dfs(node):
        if node in visited:
            return
        visited.add(node)
        for dep in graph.get(node, []):
            dfs(dep)
        order.append(node)
        
    dfs(start_package)
    return order

def generate_graphviz(graph, output_file):
    lines = ["digraph G {"]
    for node, deps in graph.items():
        if not deps:
            lines.append(f'    "{node}";')
        else:
            for dep in deps:
                lines.append(f'    "{node}" -> "{dep}";')
    lines.append("}")
    
    graphviz_code = "\n".join(lines)
    
    print("\n--- Код Graphviz ---")
    print(graphviz_code)
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(graphviz_code)
        print(f"\nФайл Graphviz сохранен: {output_file}")
    except Exception as e:
        print(f"Ошибка сохранения: {e}")

def main():
    args = parse_args()
    
    if args.depth <= 0:
        print("Ошибка: Глубина (--depth) должна быть больше 0")
        sys.exit(1)

    print("--- Параметры ---")
    print(f"package: {args.package}")
    print(f"repo: {args.repo}")
    print(f"test_mode: {args.test_mode}")
    print(f"depth: {args.depth}")
    print(f"output: {args.output}")

    if args.test_mode:
        print("\n--- Построение графа (DFS) ---")
        data = load_test_repo(args.repo)
        graph = build_graph_dfs(args.package, data, args.depth)
        
        if not graph:
            print("Граф пуст или пакет не найден.")
        else:
            for pkg, deps in graph.items():
                deps_str = ", ".join(deps) if deps else "нет"
                print(f"{pkg} -> [{deps_str}]")
                
            print("\n--- Порядок загрузки зависимостей ---")
            load_order = get_load_order(graph, args.package)
            print(" -> ".join(load_order))
                
            generate_graphviz(graph, args.output)

if __name__ == "__main__":
    main()