use serde::Serialize;
use sysinfo::System;

#[derive(Debug, Serialize)]
pub struct SystemMetrics {
    pub cpu_usage: f32,
    pub total_memory: u64, // in Bytes
    pub used_memory: u64,  // in Bytes
    pub processes: Vec<ProcessInfo>,
}

#[derive(Debug, Serialize)]
pub struct ProcessInfo {
    pub pid: u32,
    pub name: String,
    pub cpu_usage: f32,
    pub memory: u64, // in Bytes
}

pub fn get_system_metrics() -> SystemMetrics {
    let mut sys = System::new_all();
    // Refresh system resources
    sys.refresh_all();
    
    // We need to wait a brief moment to get accurate CPU readings or just read current
    let cpu_usage = sys.global_cpu_usage();
    let total_memory = sys.total_memory();
    let used_memory = sys.used_memory();

    let mut processes = Vec::new();
    for (pid, process) in sys.processes() {
        processes.push(ProcessInfo {
            pid: pid.as_u32(),
            name: process.name().to_string_lossy().to_string(),
            cpu_usage: process.cpu_usage(),
            memory: process.memory(),
        });
    }

    // Sort processes by CPU usage descending, and take top 10
    processes.sort_by(|a, b| b.cpu_usage.partial_cmp(&a.cpu_usage).unwrap_or(std::cmp::Ordering::Equal));
    processes.truncate(15);

    SystemMetrics {
        cpu_usage,
        total_memory,
        used_memory,
        processes,
    }
}
