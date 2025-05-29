import matplotlib.pyplot as plt
import numpy as np
import os
import argparse

def plot_radar(score_dict, output_dir='output', filename='radar.png', title='对象能力雷达图'):
    """
    绘制能力雷达图并保存图片。

    参数:
        score_dict: dict, 维度名称到分数的映射
        output_dir: str, 图片保存的文件夹
        filename: str, 图片文件名
        title: str, 图表标题

    返回:
        图片保存的完整路径
    """
    # 设置中文显示
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    labels = list(score_dict.keys())
    values = list(score_dict.values())
    num_vars = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

    # 闭合数据以形成环形
    values += values[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.plot(angles, values, linewidth=2, linestyle='solid', label='能力得分')
    ax.fill(angles, values, alpha=0.25)
    ax.set_thetagrids(np.degrees(angles[:-1]), labels)
    plt.title(title, size=20, pad=20)
    plt.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1))

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    save_path = os.path.join(output_dir, filename)
    plt.savefig(save_path, bbox_inches='tight')
    plt.close(fig)
    return save_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='绘制能力雷达图')
    parser.add_argument('--scores', type=str, required=True,
                        help='评分字典，格式为"{\\"维度1\\": 分数1, \\\"维度2\\": 分数2}"')
    parser.add_argument('--filename', type=str, default='radar.png',
                        help='输出文件名')
    parser.add_argument('--title', type=str, default='对象能力雷达图',
                        help='图表标题')
    args = parser.parse_args()

    try:
        # 解析评分字符串
        score_str = args.scores.replace('\\"', '"')
        score_dict = eval(score_str)
        
        # 绘制雷达图
        path = plot_radar(score_dict, filename=args.filename, title=args.title)
        print(f"图片已保存到: {path}")
    except Exception as e:
        print(f"发生错误: {str(e)}")