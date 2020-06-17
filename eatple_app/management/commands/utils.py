import psutil
import datetime


def get_hw_idle_info():
    """CPU, 메모리, 디스크의 예비율 정보를 구한다 """
    print('TIME :', datetime.datetime.now())

    rst = dict()  # 반환값 초기화

    cp = psutil.cpu_times_percent(interval=None, percpu=False)  # CPU 데이터
    cp_item = dict()
    cp_item['free'] = psutil.cpu_count(
        logical=False) * (cp.idle/100)  # Physical
    cp_item['idle'] = cp.idle
    cp_item['desc'] = f"Idle CPU: {cp_item['free']:.2f} core ({cp_item['idle']}%)"
    rst['cpu'] = cp_item

    vm = psutil.virtual_memory()  # 메모리 데이터
    vm_item = dict()
    vm_item['free'] = vm.available//(1024*1024)
    vm_item['idle'] = vm.available/vm.total*100
    vm_item['desc'] = f"Idle Memory: {vm_item['free']:,}MB ({vm_item['idle']:.1f}%)"
    rst['memory'] = vm_item

    du = psutil.disk_usage(path='/')  # 디스크 데이터
    du_item = dict()
    du_item['free'] = du.free//(1024*1024)
    du_item['idle'] = du.free/du.total*100
    du_item['desc'] = f"Idle Disk: {du_item['free']:,}MB ({du_item['idle']:.1f}%)"
    rst['disk'] = du_item

    return rst
