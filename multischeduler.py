from apscheduler.schedulers.blocking import BlockingScheduler
import requests
import threading
import json
import time
import sys
import datetime

def run_scheduler(class_ids, x_date, x_jwt_token, x_token, early=100):
    url = 'https://pure360-api.pure-yoga.cn/api/v3/booking'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Origin': 'https://pure360.pure-yoga.cn',
        'Referer': 'https://pure360.pure-yoga.cn/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'X-Date': x_date,
        'X-Features': 'last_chance_booking',
        'X-JWT-Token': x_jwt_token,
        'X-Token': x_token,
        'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
    }

    def job(early):
        time.sleep(1-early/1000)
        
        # Calculate the cutoff time (9:00:00 AM)
        now = datetime.datetime.now()
        cutoff_time = now.replace(hour=9, minute=0, second=0, microsecond=0)
        
        for class_id in class_ids:
            data = {
                'language_id': '3',
                'class_id': class_id,
                'book_type': 1,
                'booked_from': 'WEB',
                'region_id': '4'
            }
            
            max_retries = 10
            retry_count = 0
            booking_success = False
            
            while retry_count < max_retries and datetime.datetime.now() < cutoff_time and not booking_success:
                if retry_count > 0:
                    print(f"重试第 {retry_count} 次预约课程 {class_id}...")
                    # Wait 50ms before retrying
                    time.sleep(0.05)
                
                before = time.time()
                response = requests.post(url, headers=headers, data=json.dumps(data))
                after = time.time()
                
                response_json = response.json()
                error_code = response_json.get('error', {}).get('code')
                
                if response.status_code == 200:
                    if error_code == 200:
                        waiting_number = response_json.get('data', {}).get('waiting_number', 'N/A')
                        print(f"抢课成功, 课程编号: {class_id}, 等待编号: {waiting_number}")
                        booking_success = True
                    elif error_code == 419:
                        print(f"你已预约此课程, 编号: {class_id}")
                        booking_success = True
                    elif error_code == 424:
                        print(f"此课堂的上课时间与您已预约的其他课堂/工作坊/活动时间重叠。如果您在应用程序内找不到该记录, 请向PURE团队查询。课程编号: {class_id}")
                        booking_success = True
                    else:
                        # Other error codes that we should retry
                        print(f"预约失败, 课程编号: {class_id}, 错误代码: {error_code}")
                else:
                    print(f"课程编号: {class_id}, 无法预约, 请确认课程编号是否正确")
                
                print(response.text)
                print(f"发送请求总耗时: {after - before}s")
                
                # Increment retry counter if booking was not successful
                if not booking_success:
                    retry_count += 1
            
            if not booking_success:
                print(f"课程 {class_id} 尝试 {retry_count} 次后仍未成功预约")
        
        threading.Thread(target=scheduler.shutdown).start()

    scheduler = BlockingScheduler()
    hour = 8
    minute = 59
    second = 59

    print(f"将在{hour}时{minute}分{second}秒{1000-early}毫秒开始抢课, 课程编号是{class_ids}")
    print("请确保课程编号和手环编号正确, 已经开始运行")
    print(f"如果预约失败，将会尝试最多重试 10 次，每次间隔 50 毫秒，直到 9:00:00")
    scheduler.add_job(job, 'cron', hour=hour, minute=minute, second=second, misfire_grace_time=60, args=[early])
    scheduler.start()
    
    print("\n抢课程序已完成，按回车键退出...")
    input()

if __name__ == "__main__":
    # This section will only run if the script is run directly (not imported)
    if len(sys.argv) > 1:
        class_ids = json.loads(sys.argv[1])
        x_date = sys.argv[2]
        x_jwt_token = sys.argv[3]
        x_token = sys.argv[4]
        early = int(sys.argv[5]) if len(sys.argv) > 5 else 100
        run_scheduler(class_ids, x_date, x_jwt_token, x_token, early)
