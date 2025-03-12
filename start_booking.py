import json
import subprocess
import sys

def get_class_ids():
    class_ids = []
    print("请输入课程编号 (每次输入一个, 直接按回车结束输入):")
    while True:
        class_id = input("课程编号(回车结束输入):").strip()
        if not class_id:
            break
        try:
            class_ids.append(int(class_id))
            if len(class_id) != 6:
                print("课程编号为6位数字, 请重新输入")
                class_ids.pop()
                break
        except ValueError:
            print("请输入有效的数字!")
    return class_ids

def main():
    # Get class IDs
    class_ids = get_class_ids()
    if not class_ids:
        print("错误: 至少需要输入一个课程编号!")
        input("按回车键退出...")
        return

    # Get X-Date
    x_date = input("请输入 X-Date: ").strip()
    if not x_date:
        print("错误: X-Date 不能为空!")
        input("按回车键退出...")
        return

    # Get X-JWT-Token
    x_jwt_token = input("请输入 X-JWT-Token: ").strip()
    if not x_jwt_token:
        print("错误: X-JWT-Token 不能为空!")
        input("按回车键退出...")
        return

    # Get X-Token
    x_token = input("请输入 X-Token: ").strip()
    if not x_token:
        print("错误: X-Token 不能为空!")
        input("按回车键退出...")
        return

    # Get early milliseconds
    early = input("提前多少毫秒抢课 (直接按回车使用默认值100毫秒): ").strip()
    if not early:
        early = "100"
    try:
        early = int(early)
    except ValueError:
        print("错误: 请输入有效的数字!")
        input("按回车键退出...")
        return

    # Convert class_ids to JSON string
    class_ids_json = json.dumps(class_ids)

    # Run the main scheduler script
    try:
        subprocess.run([sys.executable, "multischeduler.py", 
                       class_ids_json, x_date, x_jwt_token, x_token, str(early)],
                      check=True)
    except subprocess.CalledProcessError as e:
        print(f"运行出错: {e}")
    except Exception as e:
        print(f"发生错误: {e}")
    
    input("按回车键退出...")

if __name__ == "__main__":
    main() 