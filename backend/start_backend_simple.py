#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TrainPPTAgent 后端服务启动脚本 (极简版)
专为已配置conda环境的用户设计，不进行任何环境检查
所有服务日志将输出到同一个日志文件中，方便监控
"""

import os
import sys
import time
import signal
import subprocess
from pathlib import Path
from typing import Dict
from datetime import datetime
from dotenv import dotenv_values
import platform

class SimpleBackendStarter:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.logs_dir = self.base_dir / 'logs'
        self.services = {
            'main_api': {
                'port': 6800,
                'dir': self.base_dir / 'main_api',
                'script': 'main.py'
            },
            'simpleOutline': {
                'port': 10001,
                'dir': self.base_dir / 'simpleOutline',
                'script': 'main_api.py'
            },
            'slide_agent': {
                'port': 10011,
                'dir': self.base_dir / 'slide_agent',
                'script': 'main_api.py'
            }
        }
        self.processes = {}
        self.log_file = None
        
    def setup_logs_directory(self):
        """设置日志目录和统一日志文件"""
        # 创建logs目录
        if not self.logs_dir.exists():
            self.logs_dir.mkdir(parents=True, exist_ok=True)
            
        # 创建统一的日志文件
        # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.logs_dir / f"train_ppt.log"
        print(f"📝 统一日志文件: {self.log_file}")
            
    def start_service(self, service_name: str, config: dict):
        """启动单个服务"""
        service_dir = config['dir']
        script = config['script']
        
        try:
            # 切换到服务目录
            os.chdir(service_dir)
            
            # 以追加模式打开统一日志文件
            log_f = open(self.log_file, 'a', encoding='utf-8')
            
            # 写入服务启动信息
            log_f.write(f"\n{'='*50}\n")
            log_f.write(f"🚀 启动服务: {service_name}\n")
            log_f.write(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            log_f.write(f"工作目录: {service_dir}\n")
            log_f.write(f"脚本文件: {script}\n")
            log_f.write(f"端口: {config['port']}\n")
            log_f.write(f"{'='*50}\n\n")
            log_f.flush()
            
            # 读取 .env 并合入当前环境
            env = os.environ.copy()
            env_file_path = service_dir / '.env'
            if env_file_path.exists():
                env.update(dotenv_values(str(env_file_path)))
            
            # 启动进程，将stdout和stderr都重定向到统一日志文件
            process = subprocess.Popen(
                [sys.executable, script],
                stdout=log_f,
                stderr=log_f,
                text=True,
                env=env,
                bufsize=1,
                universal_newlines=True
            )
            
            # 等待一段时间检查进程是否正常启动
            time.sleep(2)
            
            if process.poll() is None:
                print(f"✅ {service_name} 启动成功 (PID: {process.pid})")
                return process, log_f  # 返回文件句柄以便后续管理
            else:
                print(f"❌ {service_name} 启动失败，请查看日志文件: {self.log_file}")
                log_f.close()
                return None, None
                    
        except Exception as e:
            print(f"❌ 启动 {service_name} 时出错: {e}")
            if 'log_f' in locals():
                log_f.close()
            return None, None
        finally:
            # 切换回原目录
            os.chdir(self.base_dir)
            
    def start_all_services(self):
        """启动所有服务"""
        print("🚀 启动所有后端服务...")
        
        # 存储文件句柄以便后续关闭
        self.log_files_handles = {}
        
        # 启动所有服务
        for service_name, config in self.services.items():
            process, log_handle = self.start_service(service_name, config)
            if process:
                self.processes[service_name] = process
                self.log_files_handles[service_name] = log_handle
            else:
                print(f"❌ 服务 {service_name} 启动失败")
                self.stop_all_services()
                return False
                
        print("🎉 所有后端服务启动成功!")
        print("📋 服务地址:")
        for service_name, config in self.services.items():
            print(f"  ✅ {service_name}: http://127.0.0.1:{config['port']}")
        print(f"📝 统一日志文件: {self.log_file}")
        
        # 根据操作系统提供不同的日志查看建议
        system = platform.system()
        if system == "Windows":
            print("💡 您可以使用以下命令实时查看日志:")
            print(f"   PowerShell: Get-Content -Path \"{self.log_file}\" -Wait")
            print(f"   CMD: type \"{self.log_file}\" | more")
        else:
            print("💡 您可以使用以下命令实时查看日志:")
            print(f"   tail -f {self.log_file}")
        print("💡 按 Ctrl+C 停止所有服务")
        
        return True
                
    def stop_all_services(self):
        """停止所有服务"""
        print("🛑 停止所有服务...")
        
        # 先关闭所有文件句柄
        for service_name, log_handle in self.log_files_handles.items():
            try:
                log_handle.close()
            except:
                pass
        
        # 再终止所有进程
        for service_name, process in self.processes.items():
            try:
                process.terminate()
                process.wait(timeout=3)
            except:
                try:
                    process.kill()
                except:
                    pass
                
        self.processes.clear()
        print("✅ 所有服务已停止")
        
    def run(self):
        """主运行函数"""
        print("=" * 60)
        print("🚀 TrainPPTAgent 后端服务启动器 (极简版 - 统一日志)")
        print("=" * 60)
        
        # 设置日志目录和统一日志文件
        self.setup_logs_directory()
        
        # 启动所有服务
        if not self.start_all_services():
            return
            
        # 等待所有进程
        try:
            while self.processes:
                for service_name, process in list(self.processes.items()):
                    if process.poll() is not None:
                        print(f"⚠️  服务 {service_name} 已停止")
                        # 关闭对应的日志文件句柄
                        if service_name in self.log_files_handles:
                            try:
                                self.log_files_handles[service_name].close()
                                del self.log_files_handles[service_name]
                            except:
                                pass
                        del self.processes[service_name]
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 收到停止信号...")
            self.stop_all_services()

def main():
    """主函数"""
    starter = SimpleBackendStarter()
    
    # 注册信号处理器
    def signal_handler(signum, frame):
        starter.stop_all_services()
        sys.exit(0)
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        starter.run()
    except KeyboardInterrupt:
        starter.stop_all_services()

if __name__ == "__main__":
    main()