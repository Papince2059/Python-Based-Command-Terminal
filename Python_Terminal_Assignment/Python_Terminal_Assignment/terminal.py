#!/usr/bin/env python3
"""
Python-Based Command Terminal
A fully functioning terminal that mimics real system terminal behavior
"""

import os
import sys
import shutil
import subprocess
import platform
import psutil
import time
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

class PythonTerminal:
    def __init__(self):
        self.current_dir = os.getcwd()
        self.command_history = []
        self.environment_vars = dict(os.environ)
        self.aliases = {}
        self.processes = {}
        
        # Initialize built-in commands
        self.builtin_commands = {
            'cd': self.cmd_cd,
            'pwd': self.cmd_pwd,
            'ls': self.cmd_ls,
            'dir': self.cmd_ls,  # Windows compatibility
            'mkdir': self.cmd_mkdir,
            'rmdir': self.cmd_rmdir,
            'rm': self.cmd_rm,
            'cp': self.cmd_cp,
            'mv': self.cmd_mv,
            'cat': self.cmd_cat,
            'echo': self.cmd_echo,
            'touch': self.cmd_touch,
            'find': self.cmd_find,
            'grep': self.cmd_grep,
            'ps': self.cmd_ps,
            'top': self.cmd_top,
            'kill': self.cmd_kill,
            'env': self.cmd_env,
            'export': self.cmd_export,
            'history': self.cmd_history,
            'clear': self.cmd_clear,
            'exit': self.cmd_exit,
            'help': self.cmd_help,
            'whoami': self.cmd_whoami,
            'date': self.cmd_date,
            'uptime': self.cmd_uptime,
            'df': self.cmd_df,
            'free': self.cmd_free,
            'alias': self.cmd_alias,
            'unalias': self.cmd_unalias,
        }
    
    def parse_command(self, command_line: str) -> List[str]:
        """Parse command line into tokens, handling quotes and escapes"""
        if not command_line.strip():
            return []
        
        # Simple tokenization that handles quotes
        tokens = []
        current_token = ""
        in_quotes = False
        quote_char = None
        
        i = 0
        while i < len(command_line):
            char = command_line[i]
            
            if char in ['"', "'"] and not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
            elif char == ' ' and not in_quotes:
                if current_token:
                    tokens.append(current_token)
                    current_token = ""
            else:
                current_token += char
            
            i += 1
        
        if current_token:
            tokens.append(current_token)
        
        return tokens
    
    def execute_command(self, command_line: str) -> str:
        """Execute a command and return the output"""
        try:
            # Add to history
            if command_line.strip():
                self.command_history.append(command_line)
            
            tokens = self.parse_command(command_line)
            if not tokens:
                return ""
            
            cmd = tokens[0]
            args = tokens[1:] if len(tokens) > 1 else []
            
            # Check for aliases
            if cmd in self.aliases:
                cmd = self.aliases[cmd]
            
            # Execute built-in commands
            if cmd in self.builtin_commands:
                return self.builtin_commands[cmd](args)
            
            # Execute external commands
            return self.execute_external_command(cmd, args)
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def execute_external_command(self, cmd: str, args: List[str]) -> str:
        """Execute external system commands"""
        try:
            full_command = [cmd] + args
            result = subprocess.run(
                full_command,
                cwd=self.current_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\nError: {result.stderr}"
            
            return output.strip()
            
        except subprocess.TimeoutExpired:
            return "Error: Command timed out"
        except FileNotFoundError:
            return f"Error: Command '{cmd}' not found"
        except Exception as e:
            return f"Error: {str(e)}"
    
    # Built-in command implementations
    def cmd_cd(self, args: List[str]) -> str:
        """Change directory"""
        if not args:
            target = os.path.expanduser("~")
        elif args[0] == "-":
            target = self.environment_vars.get("OLDPWD", self.current_dir)
        else:
            target = args[0]
        
        target = os.path.expanduser(target)
        if not os.path.isabs(target):
            target = os.path.join(self.current_dir, target)
        
        try:
            target = os.path.abspath(target)
            if os.path.exists(target) and os.path.isdir(target):
                self.environment_vars["OLDPWD"] = self.current_dir
                self.current_dir = target
                os.chdir(target)
                return ""
            else:
                return f"cd: {target}: No such file or directory"
        except Exception as e:
            return f"cd: {str(e)}"
    
    def cmd_pwd(self, args: List[str]) -> str:
        """Print working directory"""
        return self.current_dir
    
    def cmd_ls(self, args: List[str]) -> str:
        """List directory contents"""
        show_hidden = "-a" in args or "--all" in args
        long_format = "-l" in args or "--long" in args
        
        # Remove flags from args to get path
        paths = [arg for arg in args if not arg.startswith("-")]
        target_path = paths[0] if paths else self.current_dir
        
        try:
            if not os.path.exists(target_path):
                return f"ls: {target_path}: No such file or directory"
            
            if os.path.isfile(target_path):
                items = [os.path.basename(target_path)]
                target_path = os.path.dirname(target_path)
            else:
                items = os.listdir(target_path)
            
            if not show_hidden:
                items = [item for item in items if not item.startswith('.')]
            
            items.sort()
            
            if long_format:
                result = []
                for item in items:
                    item_path = os.path.join(target_path, item)
                    try:
                        stat = os.stat(item_path)
                        size = stat.st_size
                        mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%b %d %H:%M")
                        is_dir = "d" if os.path.isdir(item_path) else "-"
                        permissions = oct(stat.st_mode)[-3:]
                        result.append(f"{is_dir}rwxr-xr-x 1 user user {size:8} {mtime} {item}")
                    except:
                        result.append(f"?????????? ? ?    ?    ?        ? ? {item}")
                return "\n".join(result)
            else:
                return "  ".join(items)
                
        except Exception as e:
            return f"ls: {str(e)}"
    
    def cmd_mkdir(self, args: List[str]) -> str:
        """Create directories"""
        if not args:
            return "mkdir: missing operand"
        
        create_parents = "-p" in args or "--parents" in args
        dirs = [arg for arg in args if not arg.startswith("-")]
        
        results = []
        for dir_name in dirs:
            try:
                if create_parents:
                    os.makedirs(dir_name, exist_ok=True)
                else:
                    os.mkdir(dir_name)
            except FileExistsError:
                results.append(f"mkdir: {dir_name}: File exists")
            except Exception as e:
                results.append(f"mkdir: {dir_name}: {str(e)}")
        
        return "\n".join(results)
    
    def cmd_rmdir(self, args: List[str]) -> str:
        """Remove empty directories"""
        if not args:
            return "rmdir: missing operand"
        
        results = []
        for dir_name in args:
            try:
                os.rmdir(dir_name)
            except OSError as e:
                results.append(f"rmdir: {dir_name}: {str(e)}")
        
        return "\n".join(results)
    
    def cmd_rm(self, args: List[str]) -> str:
        """Remove files and directories"""
        if not args:
            return "rm: missing operand"
        
        recursive = "-r" in args or "-R" in args or "--recursive" in args
        force = "-f" in args or "--force" in args
        files = [arg for arg in args if not arg.startswith("-")]
        
        results = []
        for file_path in files:
            try:
                if os.path.isdir(file_path):
                    if recursive:
                        shutil.rmtree(file_path)
                    else:
                        results.append(f"rm: {file_path}: is a directory")
                else:
                    os.remove(file_path)
            except FileNotFoundError:
                if not force:
                    results.append(f"rm: {file_path}: No such file or directory")
            except Exception as e:
                results.append(f"rm: {file_path}: {str(e)}")
        
        return "\n".join(results)
    
    def cmd_cp(self, args: List[str]) -> str:
        """Copy files and directories"""
        if len(args) < 2:
            return "cp: missing operand"
        
        recursive = "-r" in args or "-R" in args or "--recursive" in args
        files = [arg for arg in args if not arg.startswith("-")]
        
        if len(files) < 2:
            return "cp: missing destination"
        
        source_files = files[:-1]
        destination = files[-1]
        
        results = []
        for source in source_files:
            try:
                if os.path.isdir(source):
                    if recursive:
                        dest_path = os.path.join(destination, os.path.basename(source)) if os.path.isdir(destination) else destination
                        shutil.copytree(source, dest_path)
                    else:
                        results.append(f"cp: {source}: is a directory (not copied)")
                else:
                    if os.path.isdir(destination):
                        shutil.copy2(source, destination)
                    else:
                        shutil.copy2(source, destination)
            except Exception as e:
                results.append(f"cp: {str(e)}")
        
        return "\n".join(results)
    
    def cmd_mv(self, args: List[str]) -> str:
        """Move/rename files and directories"""
        if len(args) < 2:
            return "mv: missing operand"
        
        source = args[0]
        destination = args[1]
        
        try:
            shutil.move(source, destination)
            return ""
        except Exception as e:
            return f"mv: {str(e)}"
    
    def cmd_cat(self, args: List[str]) -> str:
        """Display file contents"""
        if not args:
            return "cat: missing operand"
        
        results = []
        for file_path in args:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    results.append(f.read())
            except Exception as e:
                results.append(f"cat: {file_path}: {str(e)}")
        
        return "\n".join(results)
    
    def cmd_echo(self, args: List[str]) -> str:
        """Display text"""
        return " ".join(args)
    
    def cmd_touch(self, args: List[str]) -> str:
        """Create empty files or update timestamps"""
        if not args:
            return "touch: missing operand"
        
        results = []
        for file_path in args:
            try:
                Path(file_path).touch()
            except Exception as e:
                results.append(f"touch: {file_path}: {str(e)}")
        
        return "\n".join(results)
    
    def cmd_find(self, args: List[str]) -> str:
        """Find files and directories"""
        if not args:
            path = self.current_dir
            pattern = "*"
        elif len(args) == 1:
            if os.path.exists(args[0]):
                path = args[0]
                pattern = "*"
            else:
                path = self.current_dir
                pattern = args[0]
        else:
            path = args[0]
            pattern = args[1]
        
        results = []
        try:
            for root, dirs, files in os.walk(path):
                for name in dirs + files:
                    if pattern == "*" or pattern in name:
                        results.append(os.path.join(root, name))
        except Exception as e:
            return f"find: {str(e)}"
        
        return "\n".join(results)
    
    def cmd_grep(self, args: List[str]) -> str:
        """Search for patterns in files"""
        if len(args) < 2:
            return "grep: missing operand"
        
        pattern = args[0]
        files = args[1:]
        
        results = []
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    for line_num, line in enumerate(f, 1):
                        if re.search(pattern, line, re.IGNORECASE):
                            results.append(f"{file_path}:{line_num}:{line.strip()}")
            except Exception as e:
                results.append(f"grep: {file_path}: {str(e)}")
        
        return "\n".join(results)
    
    def cmd_ps(self, args: List[str]) -> str:
        """List running processes"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            result = ["PID\tNAME\t\tCPU%\tMEM%"]
            for proc in processes[:20]:  # Limit to first 20 processes
                result.append(f"{proc['pid']}\t{proc['name'][:15]:<15}\t{proc['cpu_percent']:.1f}\t{proc['memory_percent']:.1f}")
            
            return "\n".join(result)
        except Exception as e:
            return f"ps: {str(e)}"
    
    def cmd_top(self, args: List[str]) -> str:
        """Display system resource usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            result = [
                f"System Resource Usage:",
                f"CPU Usage: {cpu_percent}%",
                f"Memory Usage: {memory.percent}% ({memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB)",
                f"Disk Usage: {disk.percent}% ({disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB)",
                "",
                "Top Processes:"
            ]
            
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            
            result.append("PID\tNAME\t\tCPU%\tMEM%")
            for proc in processes[:10]:
                result.append(f"{proc['pid']}\t{proc['name'][:15]:<15}\t{proc['cpu_percent'] or 0:.1f}\t{proc['memory_percent'] or 0:.1f}")
            
            return "\n".join(result)
        except Exception as e:
            return f"top: {str(e)}"
    
    def cmd_kill(self, args: List[str]) -> str:
        """Kill a process by PID"""
        if not args:
            return "kill: missing operand"
        
        try:
            pid = int(args[0])
            process = psutil.Process(pid)
            process.terminate()
            return f"Process {pid} terminated"
        except ValueError:
            return "kill: invalid PID"
        except psutil.NoSuchProcess:
            return f"kill: no process with PID {args[0]}"
        except psutil.AccessDenied:
            return f"kill: permission denied for PID {args[0]}"
        except Exception as e:
            return f"kill: {str(e)}"
    
    def cmd_env(self, args: List[str]) -> str:
        """Display environment variables"""
        if not args:
            return "\n".join([f"{k}={v}" for k, v in self.environment_vars.items()])
        else:
            var_name = args[0]
            return self.environment_vars.get(var_name, f"env: {var_name}: not found")
    
    def cmd_export(self, args: List[str]) -> str:
        """Set environment variables"""
        if not args:
            return "export: missing operand"
        
        for arg in args:
            if "=" in arg:
                key, value = arg.split("=", 1)
                self.environment_vars[key] = value
                os.environ[key] = value
            else:
                return f"export: invalid format '{arg}'"
        
        return ""
    
    def cmd_history(self, args: List[str]) -> str:
        """Show command history"""
        if not self.command_history:
            return ""
        
        result = []
        for i, cmd in enumerate(self.command_history[-20:], 1):  # Show last 20 commands
            result.append(f"{i:3} {cmd}")
        
        return "\n".join(result)
    
    def cmd_clear(self, args: List[str]) -> str:
        """Clear the screen"""
        return "\033[2J\033[H"  # ANSI escape codes for clear screen
    
    def cmd_exit(self, args: List[str]) -> str:
        """Exit the terminal"""
        return "EXIT"
    
    def cmd_help(self, args: List[str]) -> str:
        """Show available commands"""
        commands = sorted(self.builtin_commands.keys())
        return f"Available commands:\n{', '.join(commands)}"
    
    def cmd_whoami(self, args: List[str]) -> str:
        """Show current user"""
        return os.getenv('USER', os.getenv('USERNAME', 'user'))
    
    def cmd_date(self, args: List[str]) -> str:
        """Show current date and time"""
        return datetime.now().strftime("%a %b %d %H:%M:%S %Z %Y")
    
    def cmd_uptime(self, args: List[str]) -> str:
        """Show system uptime"""
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            return f"up {uptime.days} days, {uptime.seconds//3600} hours, {(uptime.seconds//60)%60} minutes"
        except:
            return "uptime: unable to get system uptime"
    
    def cmd_df(self, args: List[str]) -> str:
        """Show disk space usage"""
        try:
            disk = psutil.disk_usage('/')
            total_gb = disk.total / (1024**3)
            used_gb = disk.used / (1024**3)
            free_gb = disk.free / (1024**3)
            
            return f"Filesystem\tSize\tUsed\tAvail\tUse%\n/\t\t{total_gb:.1f}G\t{used_gb:.1f}G\t{free_gb:.1f}G\t{disk.percent:.0f}%"
        except Exception as e:
            return f"df: {str(e)}"
    
    def cmd_free(self, args: List[str]) -> str:
        """Show memory usage"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            total_mb = memory.total / (1024**2)
            used_mb = memory.used / (1024**2)
            free_mb = memory.available / (1024**2)
            
            swap_total_mb = swap.total / (1024**2)
            swap_used_mb = swap.used / (1024**2)
            swap_free_mb = swap.free / (1024**2)
            
            result = [
                "Type\t\tTotal\t\tUsed\t\tFree",
                f"Mem:\t\t{total_mb:.0f}MB\t\t{used_mb:.0f}MB\t\t{free_mb:.0f}MB",
                f"Swap:\t\t{swap_total_mb:.0f}MB\t\t{swap_used_mb:.0f}MB\t\t{swap_free_mb:.0f}MB"
            ]
            
            return "\n".join(result)
        except Exception as e:
            return f"free: {str(e)}"
    
    def cmd_alias(self, args: List[str]) -> str:
        """Create command aliases"""
        if not args:
            return "\n".join([f"{k}='{v}'" for k, v in self.aliases.items()])
        
        for arg in args:
            if "=" in arg:
                alias, command = arg.split("=", 1)
                self.aliases[alias] = command.strip("'\"")
            else:
                return f"alias: invalid format '{arg}'"
        
        return ""
    
    def cmd_unalias(self, args: List[str]) -> str:
        """Remove command aliases"""
        if not args:
            return "unalias: missing operand"
        
        for alias in args:
            if alias in self.aliases:
                del self.aliases[alias]
            else:
                return f"unalias: {alias}: not found"
        
        return ""
    
    def get_prompt(self) -> str:
        """Generate command prompt"""
        user = self.cmd_whoami([])
        hostname = platform.node()
        current_dir = os.path.basename(self.current_dir) or self.current_dir
        return f"{user}@{hostname}:{current_dir}$ "
    
    def run(self):
        """Main terminal loop"""
        print("Python Terminal v1.0")
        print(f"Running on {platform.system()} {platform.release()}")
        print("Type 'help' for available commands or 'exit' to quit.\n")
        
        while True:
            try:
                prompt = self.get_prompt()
                command = input(prompt).strip()
                
                if not command:
                    continue
                
                output = self.execute_command(command)
                
                if output == "EXIT":
                    print("Goodbye!")
                    break
                elif output:
                    print(output)
                    
            except KeyboardInterrupt:
                print("\n^C")
                continue
            except EOFError:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Terminal error: {str(e)}")

def main():
    """Entry point for the terminal"""
    terminal = PythonTerminal()
    terminal.run()

if __name__ == "__main__":
    main()