#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TrainPPTAgent 后端服务启动脚本
简化版 - 不检查依赖环境，用户自行管理conda环境
支持将所有服务日志输出到同一个日志文件中
"""

import os
import sys
import time
import signal
import subprocess
import shutil
import argparse
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import dotenv_values
import platform

class BackendStarter:
    def __init__(self, unified_logging=False):
        self.base_dir = Path(__file__).parent
        self.logs_dir = self.base_dir / 'logs'
        self.unified_logging = unified_logging
        self.services = {
            'main_api': {
                'port': 6800,
                'dir': self.base_dir / 'main_api',
                'script': 'main.py',
                'env_file': '.env',
                'env_template': 'env_template'
            },
            'simpleOutline': {
                'port': 10001,
                'dir': self.base_dir / 'simpleOutline',
                'script': 'main_api.py',
                'env_file': '.env',
                'env_template': 'env_template'
            },
            'slide_agent': {
                'port': 10011,
                'dir': self.base_dir / 'slide_agent',
                'script': 'main_api.py',
                'env_file': '.env',
                'env_template': 'env_template'
            }
        }
        self.processes: Dict[str, subprocess.Popen] = {}
        self.log_files: Dict[str, Path] = {}
        self.log_file_handles: Dict[str, object] = {}
        self.unified_log_file: Optional[Path] = None
        
    def setup_logs_directory(self):
        """设置日志目录"""
        print("📁 设置日志目录...")
        
        # 创建logs目录
        if not self.logs_dir.exists():
            self.logs_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ 创建日志目录: {self.logs_dir}")
        else:
            print(f"✅ 日志目录已存在: {self.logs_dir}")
            
        if self.unified_logging:
            # 创建统一的日志文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.unified_log_file = self.logs_dir / f"all_services_{timestamp}.log"
            print(f"📝 统一日志文件: {self.unified_log_file}")
        else:
            # 为每个服务创建单独的日志文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            for service_name in self.services.keys():
                log_file = self.logs_dir / f"{service_name}_{timestamp}.log"
                self.log_files[service_name] = log_file
                print(f"📝 日志文件: {service_name} -> {log_file}")
            
    def print_banner(self):
        """打印启动横幅"""
        print("=" * 60)
        print("🚀 TrainPPTAgent 后端服务启动器 (简化版)")
        if self.unified_logging:
            print("📝 所有服务日志将输出到同一个日志文件中")
        print("=" * 60)
        print()
        
    def check_ports(self) -> List[int]:
        """检查端口占用情况"""
        occupied_ports = []
        for service_name, config in self.services.items():
            port = config['port']
            try:
                # 检查端口是否被占用
                import socket
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    if s.connect_ex(('localhost', port)) == 0:
                        occupied_ports.append(port)
            except Exception:
                pass
        return occupied_ports
        
    def kill_processes_on_ports(self, ports: List[int]):
        """杀死占用指定端口的进程"""
        if not ports:
            return
            
        print(f"🔍 发现端口占用: {ports}")
        response = input("是否清理这些端口? (y/N): ").strip().lower()
        
        if response != 'y':
            print("❌ 用户取消操作")
            sys.exit(1)
            
        killed_count = 0
        for port in ports:
            try:
                import psutil
                # 查找占用端口的进程
                for proc in psutil.process_iter(['pid', 'name', 'connections']):
                    try:
                        connections = proc.info['connections']
                        if connections:
                            for conn in connections:
                                if conn.laddr.port == port:
                                    print(f"🔄 终止进程 {proc.info['name']} (PID: {proc.info['pid']}) 占用端口 {port}")
                                    proc.terminate()
                                    proc.wait(timeout=5)
                                    killed_count += 1
                                    break
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                        continue
            except Exception as e:
                print(f"⚠️  清理端口 {port} 时出错: {e}")
                
        print(f"✅ 清理完成，终止了 {killed_count} 个进程")
        time.sleep(2)  # 等待端口释放
        
    def setup_env_files(self):
        """设置环境文件"""
        print("⚙️  设置环境文件...")
        
        for service_name, config in self.services.items():
            service_dir = config['dir']
            env_file = service_dir / config['env_file']
            env_template = service_dir / config['env_template']
            
            if not service_dir.exists():
                print(f"❌ 错误: 服务目录不存在 {service_dir}")
                sys.exit(1)
                
            if not env_template.exists():
                print(f"⚠️  警告: 环境模板文件不存在 {env_template}")
                continue
                
            if not env_file.exists():
                print(f"📝 复制环境文件: {service_name}")
                shutil.copy2(env_template, env_file)
            else:
                print(f"✅ 环境文件已存在: {service_name}")
                
    def start_service(self, service_name: str, config: Dict) -> Optional[subprocess.Popen]:
        """启动单个服务"""
        service_dir = config['dir']
        script = config['script']
        port = config['port']
        
        print(f"🚀 启动服务: {service_name} (端口: {port})")
        
        try:
            # 切换到服务目录
            os.chdir(service_dir)
            
            if self.unified_logging and self.unified_log_file:
                # 使用统一日志文件
                log_file_path = self.unified_log_file
                log_f = open(log_file_path, 'a', encoding='utf-8')
                print(f"📝 日志文件: {log_file_path}")
            else:
                # 使用单独的日志文件
                log_file_path = self.log_files[service_name]
                log_f = open(log_file_path, 'w', encoding='utf-8')
                print(f"📝 日志文件: {log_file_path}")
            
            # 写入启动信息
            log_f.write(f"\n{'='*50}\n")
            log_f.write(f"🚀 启动服务: {service_name}\n")
            log_f.write(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            log_f.write(f"工作目录: {service_dir}\n")
            log_f.write(f"脚本文件: {script}\n")
            log_f.write(f"端口: {port}\n")
            log_f.write(f"{'='*50}\n\n")
            log_f.flush()
            
            # 保存文件句柄以便后续管理
            self.log_file_handles[service_name] = log_f
            
            # 读取 .env 并合入当前环境
            env = os.environ.copy()
            env_file_path = service_dir / config['env_file']
            if env_file_path.exists():
                env.update(dotenv_values(str(env_file_path)))
            
            process = subprocess.Popen(
                [sys.executable, script],
                stdout=log_f,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                env=env  
            )
            
            # 等待一段时间检查进程是否正常启动
            time.sleep(3)
            
            if process.poll() is None:
                print(f"✅ {service_name} 启动成功 (PID: {process.pid})")
                return process
            else:
                print(f"❌ {service_name} 启动失败，请查看日志文件: {log_file_path}")
                log_f.close()
                return None
                    
        except Exception as e:
            print(f"❌ 启动 {service_name} 时出错: {e}")
            if 'log_f' in locals():
                log_f.close()
            return None
        finally:
            # 切换回原目录
            os.chdir(self.base_dir)
            
    def start_all_services(self):
        """启动所有服务"""
        print("🚀 启动所有后端服务...")
        print()
        
        # 启动所有服务
        for service_name, config in self.services.items():
            process = self.start_service(service_name, config)
            if process:
                self.processes[service_name] = process
            else:
                print(f"❌ 服务 {service_name} 启动失败，停止所有服务")
                self.stop_all_services()
                sys.exit(1)
                
        print()
        print("=" * 60)
        print("🎉 所有后端服务启动成功!")
        print("=" * 60)
        print("📋 服务状态:")
        for service_name, config in self.services.items():
            if service_name in self.processes:
                print(f"  ✅ {service_name}: http://127.0.0.1:{config['port']}")
        if self.unified_logging and self.unified_log_file:
            print(f"  📝 统一日志文件: {self.unified_log_file}")
            # 根据操作系统提供不同的日志查看建议
            system = platform.system()
            if system == "Windows":
                print("  💡 您可以使用以下命令实时查看日志:")
                print(f"     PowerShell: Get-Content -Path \"{self.unified_log_file}\" -Wait")
                print(f"     CMD: type \"{self.unified_log_file}\" | more")
            else:
                print("  💡 您可以使用以下命令实时查看日志:")
                print(f"     tail -f {self.unified_log_file}")
        else:
            print("  📝 日志文件:")
            for service_name, log_file in self.log_files.items():
                print(f"     {service_name}: {log_file}")
        print()
        print("💡 提示:")
        print("  - 按 Ctrl+C 停止所有服务")
        print("  - 前端服务请访问: http://127.0.0.1:5173")
        if self.unified_logging and self.unified_log_file:
            print("  - 所有服务日志已合并到统一日志文件中")
        print("=" * 60)
        
        # 等待所有进程
        try:
            while self.processes:
                for service_name, process in list(self.processes.items()):
                    if process.poll() is not None:
                        print(f"⚠️  服务 {service_name} 已停止")
                        # 关闭对应的日志文件句柄
                        if service_name in self.log_file_handles:
                            try:
                                self.log_file_handles[service_name].close()
                                del self.log_file_handles[service_name]
                            except:
                                pass
                        del self.processes[service_name]
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 收到停止信号，正在关闭所有服务...")
            self.stop_all_services()
            
    def stop_all_services(self):
        """停止所有服务"""
        print("🛑 停止所有服务...")
        
        # 先关闭所有文件句柄
        for service_name, log_handle in self.log_file_handles.items():
            try:
                log_handle.close()
            except:
                pass
        
        # 再终止所有进程
        for service_name, process in self.processes.items():
            try:
                print(f"🔄 停止服务: {service_name}")
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {service_name} 已停止")
            except subprocess.TimeoutExpired:
                print(f"⚠️  {service_name} 强制终止")
                process.kill()
            except Exception as e:
                print(f"❌ 停止 {service_name} 时出错: {e}")
                
        self.processes.clear()
        self.log_file_handles.clear()
        print("✅ 所有服务已停止")
        
    def run(self):
        """主运行函数"""
        self.print_banner()
        
        # 设置日志目录
        self.setup_logs_directory()
        
        # 检查端口占用
        occupied_ports = self.check_ports()
        if occupied_ports:
            self.kill_processes_on_ports(occupied_ports)
            
        # 设置环境文件
        self.setup_env_files()
        
        # 启动所有服务
        self.start_all_services()

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='TrainPPTAgent 后端服务启动器')
    parser.add_argument('--unified-logging', action='store_true', 
                        help='将所有服务日志输出到同一个日志文件中')
    args = parser.parse_args()
    
    starter = BackendStarter(unified_logging=args.unified_logging)
    
    # 注册信号处理器
    def signal_handler(signum, frame):
        print("\n🛑 收到信号，正在停止服务...")
        starter.stop_all_services()
        sys.exit(0)
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        starter.run()
    except KeyboardInterrupt:
        print("\n🛑 用户中断")
        starter.stop_all_services()
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        starter.stop_all_services()
        sys.exit(1)

if __name__ == "__main__":
    main()