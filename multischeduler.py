from apscheduler.schedulers.blocking import BlockingScheduler
import requests
import threading
import json
import time
import sys
import datetime
import concurrent.futures

def run_scheduler(class_ids, x_date, x_jwt_token, x_token, early=900, max_attempts=38):
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

    def make_booking_request(class_id, attempt_num, success_event):
        """单次尝试预约课程，接受当前尝试次数和成功事件对象"""
        if success_event.is_set():
            return  # 如果已成功预约则直接返回
            
        data = {
            'language_id': '3',
            'class_id': class_id,
            'book_type': 1,
            'booked_from': 'WEB',
            'region_id': '4'
        }
        
        print(f"课程 {class_id} - 尝试第 {attempt_num} 次预约...")
        before = time.time()
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            after = time.time()
            
            response_json = response.json()
            error_code = response_json.get('error', {}).get('code')
            
            if response.status_code == 200:
                if error_code == 200:
                    waiting_number = response_json.get('data', {}).get('waiting_number', 'N/A')
                    print(f"课程 {class_id} - 尝试 {attempt_num} - 抢课成功, 等待编号: {waiting_number}")
                    success_event.set()  # 标记为成功预约
                elif error_code == 419:
                    print(f"课程 {class_id} - 尝试 {attempt_num} - 你已预约此课程")
                    success_event.set()  # 标记为成功预约
                elif error_code == 424:
                    print(f"课程 {class_id} - 尝试 {attempt_num} - 此课堂的上课时间与您已预约的其他课堂/工作坊/活动时间重叠")
                    success_event.set()  # 标记为成功预约
                elif error_code == 426:
                    print(f"课程 {class_id} - 尝试 {attempt_num} - 目前无法进行预约, 预约时间为 9-11点")
                elif error_code == 453:
                    print(f"课程 {class_id} - 尝试 {attempt_num} - 此课堂不能经应用程序或网页预约")
                else:
                    print(f"课程 {class_id} - 尝试 {attempt_num} - 预约失败, 错误代码: {error_code}")
            else:
                print(f"课程 {class_id} - 尝试 {attempt_num} - 无法预约, HTTP状态码: {response.status_code}")
            
            print(f"课程 {class_id} - 尝试 {attempt_num} - 发送请求耗时: {after - before}s")
            
        except Exception as e:
            print(f"课程 {class_id} - 尝试 {attempt_num} - 发生错误: {e}")

    def book_single_class(class_id):
        """为单个课程发起多次并行预约尝试"""
        # 使用threading.Event作为成功预约的标志
        success_event = threading.Event()
        
        # 计算截止时间 (9:00:05 AM)
        now = datetime.datetime.now()
        cutoff_time = now.replace(hour=9, minute=0, second=1, microsecond=0)
        
        # 创建一个线程池来管理此课程的多次预约尝试
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_attempts) as executor:
            futures = []
            attempt = 0
            
            # 发起预定数量的尝试，每次间隔50ms
            while attempt < max_attempts and datetime.datetime.now() < cutoff_time:
                attempt += 1
                # 提交预约请求任务到线程池
                futures.append(executor.submit(make_booking_request, class_id, attempt, success_event))
                # 等待50毫秒再发起下一次尝试
                time.sleep(0.05)
                
                # 如果已成功预约，则不再继续尝试
                if success_event.is_set():
                    print(f"课程 {class_id} - 已成功预约，停止后续尝试")
                    break
            
            # 等待所有已提交的尝试完成
            concurrent.futures.wait(futures)
        
        return success_event.is_set()

    def job(early):
        time.sleep(1-early/1000)
        
        # 使用线程池为每个课程并行执行预约
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(class_ids)) as executor:
            # 提交所有课程的预约任务
            futures = {executor.submit(book_single_class, class_id): class_id for class_id in class_ids}
            
            # 等待所有课程预约完成
            for future in concurrent.futures.as_completed(futures):
                class_id = futures[future]
                try:
                    success = future.result()
                    if success:
                        print(f"课程 {class_id} 预约成功完成")
                    else:
                        print(f"课程 {class_id} 预约未成功")
                except Exception as e:
                    print(f"课程 {class_id} 预约过程中发生异常: {e}")
        
        threading.Thread(target=scheduler.shutdown).start()

    scheduler = BlockingScheduler()
    hour = 8
    minute = 59
    second = 59

    print(f"将在{hour}时{minute}分{second}秒{1000-early}毫秒开始抢课, 课程编号是{class_ids}")
    print(f"每个课程将同时发起最多{max_attempts}次并行预约尝试，每次间隔50毫秒")
    print(f"所有课程将同时并行预约，互不影响")
    print(f"预约截止时间为9点01秒")
    scheduler.add_job(job, 'cron', hour=hour, minute=minute, second=second, misfire_grace_time=60, args=[early])
    scheduler.start()
    
    print("\n抢课程序已完成, 按回车键退出...")
    input()

if __name__ == "__main__":
    # This section will only run if the script is run directly (not imported)
    if len(sys.argv) > 1:
        class_ids = json.loads(sys.argv[1])
        x_date = sys.argv[2]
        x_jwt_token = sys.argv[3]
        x_token = sys.argv[4]
        early = int(sys.argv[5]) if len(sys.argv) > 5 else 100
        max_attempts = int(sys.argv[6]) if len(sys.argv) > 6 else 38  # 默认最多尝试38次
        run_scheduler(class_ids, x_date, x_jwt_token, x_token, early, max_attempts)
