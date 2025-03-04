#!/usr/bin/env python3
"""
Performance testing for API endpoints and database queries.

This script measures the performance of API endpoints and the underlying database
queries to identify potential bottlenecks and optimization opportunities.

The test simulates different load scenarios:
1. Light load (few concurrent users)
2. Medium load (moderate concurrent users)
3. Heavy load (many concurrent users)

For each scenario, it measures response times, throughput, and resource utilization.
"""

import asyncio
import time
import statistics
import argparse
import aiohttp
import psutil
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

# Configuration
BASE_URL = "http://localhost:8000"
TEST_ENDPOINTS = [
    "/api/health",
    "/api/knowledge-graph/entities",
    "/api/knowledge-graph/relationships",
    "/api/research?limit=10&page=1",
    "/api/implementation?limit=10&page=1"
]

# Test scenarios
LIGHT_LOAD = 5    # 5 concurrent users
MEDIUM_LOAD = 20  # 20 concurrent users
HEAVY_LOAD = 50   # 50 concurrent users

# Test duration
TEST_DURATION = 30  # 30 seconds per scenario

@dataclass
class RequestResult:
    """Store the result of a single API request."""
    endpoint: str
    status_code: int
    response_time: float
    error: Optional[str] = None

@dataclass
class EndpointStats:
    """Statistics for a single endpoint."""
    endpoint: str
    request_count: int
    success_count: int
    failure_count: int
    min_response_time: float
    max_response_time: float
    avg_response_time: float
    p95_response_time: float  # 95th percentile
    p99_response_time: float  # 99th percentile

@dataclass
class ScenarioResult:
    """Results for a load testing scenario."""
    scenario_name: str
    concurrent_users: int
    duration: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    requests_per_second: float
    avg_response_time: float
    endpoint_stats: List[EndpointStats]
    cpu_usage: List[float]
    memory_usage: List[float]

class APILoadTester:
    """API load testing tool."""
    
    def __init__(self, base_url: str, endpoints: List[str]):
        """Initialize the load tester."""
        self.base_url = base_url
        self.endpoints = endpoints
        self.auth_token = None
    
    async def login(self):
        """Authenticate and get token."""
        async with aiohttp.ClientSession() as session:
            login_data = {
                "username": "admin",
                "password": "password"
            }
            try:
                async with session.post(f"{self.base_url}/api/auth/login", json=login_data) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.auth_token = data.get("access_token")
                        return True
                    else:
                        print(f"Login failed with status {response.status}")
                        return False
            except Exception as e:
                print(f"Login error: {e}")
                return False
    
    async def make_request(self, session: aiohttp.ClientSession, endpoint: str) -> RequestResult:
        """Make a single API request."""
        url = f"{self.base_url}{endpoint}"
        headers = {}
        
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        start_time = time.time()
        try:
            async with session.get(url, headers=headers) as response:
                await response.text()  # Ensure response is fully read
                end_time = time.time()
                return RequestResult(
                    endpoint=endpoint,
                    status_code=response.status,
                    response_time=(end_time - start_time) * 1000  # ms
                )
        except Exception as e:
            end_time = time.time()
            return RequestResult(
                endpoint=endpoint,
                status_code=0,
                response_time=(end_time - start_time) * 1000,
                error=str(e)
            )
    
    async def user_session(self, user_id: int, duration: int, results: List[RequestResult]):
        """Simulate a user making requests for a specified duration."""
        async with aiohttp.ClientSession() as session:
            end_time = time.time() + duration
            while time.time() < end_time:
                for endpoint in self.endpoints:
                    result = await self.make_request(session, endpoint)
                    results.append(result)
                    
                    # Small delay to prevent overwhelming the server in tests
                    await asyncio.sleep(0.1)
    
    async def run_scenario(self, name: str, concurrent_users: int, duration: int) -> ScenarioResult:
        """Run a load testing scenario with the specified number of concurrent users."""
        print(f"Running scenario: {name} with {concurrent_users} concurrent users for {duration} seconds")
        
        # Login first to get auth token
        if not self.auth_token:
            if not await self.login():
                raise Exception("Login failed, cannot continue with tests")
        
        results: List[RequestResult] = []
        cpu_usage = []
        memory_usage = []
        
        # Create monitoring task
        async def monitor_resources():
            while True:
                cpu_usage.append(psutil.cpu_percent(interval=1))
                memory_usage.append(psutil.virtual_memory().percent)
                await asyncio.sleep(1)
        
        # Start monitoring and user sessions
        monitor_task = asyncio.create_task(monitor_resources())
        
        user_tasks = [
            self.user_session(i, duration, results)
            for i in range(concurrent_users)
        ]
        
        start_time = time.time()
        await asyncio.gather(*user_tasks)
        end_time = time.time()
        
        # Stop monitoring
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass
        
        # Calculate overall statistics
        actual_duration = end_time - start_time
        total_requests = len(results)
        successful_requests = sum(1 for r in results if 200 <= r.status_code < 300)
        failed_requests = total_requests - successful_requests
        
        if total_requests > 0:
            avg_response_time = statistics.mean(r.response_time for r in results)
            requests_per_second = total_requests / actual_duration
        else:
            avg_response_time = 0
            requests_per_second = 0
        
        # Calculate per-endpoint statistics
        endpoint_stats = []
        for endpoint in self.endpoints:
            endpoint_results = [r for r in results if r.endpoint == endpoint]
            if endpoint_results:
                response_times = [r.response_time for r in endpoint_results]
                response_times.sort()
                
                p95_index = int(len(response_times) * 0.95)
                p99_index = int(len(response_times) * 0.99)
                
                endpoint_stats.append(EndpointStats(
                    endpoint=endpoint,
                    request_count=len(endpoint_results),
                    success_count=sum(1 for r in endpoint_results if 200 <= r.status_code < 300),
                    failure_count=sum(1 for r in endpoint_results if r.status_code < 200 or r.status_code >= 300),
                    min_response_time=min(response_times),
                    max_response_time=max(response_times),
                    avg_response_time=statistics.mean(response_times),
                    p95_response_time=response_times[p95_index],
                    p99_response_time=response_times[p99_index]
                ))
        
        return ScenarioResult(
            scenario_name=name,
            concurrent_users=concurrent_users,
            duration=actual_duration,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            requests_per_second=requests_per_second,
            avg_response_time=avg_response_time,
            endpoint_stats=endpoint_stats,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage
        )

def print_scenario_results(result: ScenarioResult):
    """Print the results of a load testing scenario."""
    print("\n" + "="*80)
    print(f"Scenario: {result.scenario_name}")
    print(f"Concurrent Users: {result.concurrent_users}")
    print(f"Duration: {result.duration:.2f} seconds")
    print(f"Total Requests: {result.total_requests}")
    print(f"Successful Requests: {result.successful_requests} ({result.successful_requests/result.total_requests*100:.2f}%)")
    print(f"Failed Requests: {result.failed_requests} ({result.failed_requests/result.total_requests*100:.2f}%)")
    print(f"Requests Per Second: {result.requests_per_second:.2f}")
    print(f"Average Response Time: {result.avg_response_time:.2f} ms")
    print(f"Average CPU Usage: {statistics.mean(result.cpu_usage):.2f}%")
    print(f"Average Memory Usage: {statistics.mean(result.memory_usage):.2f}%")
    
    print("\nEndpoint Statistics:")
    print(f"{'Endpoint':<40} {'Requests':<10} {'Success %':<10} {'Avg (ms)':<10} {'Min (ms)':<10} {'Max (ms)':<10} {'P95 (ms)':<10} {'P99 (ms)':<10}")
    print("-"*110)
    
    for stat in result.endpoint_stats:
        success_percent = stat.success_count / stat.request_count * 100 if stat.request_count > 0 else 0
        print(f"{stat.endpoint:<40} {stat.request_count:<10} {success_percent:<10.2f} {stat.avg_response_time:<10.2f} {stat.min_response_time:<10.2f} {stat.max_response_time:<10.2f} {stat.p95_response_time:<10.2f} {stat.p99_response_time:<10.2f}")

def generate_charts(results: List[ScenarioResult], output_dir: str = "performance_results"):
    """Generate performance charts from test results."""
    import os
    import numpy as np
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Chart 1: Requests per second by scenario
    plt.figure(figsize=(10, 6))
    scenarios = [r.scenario_name for r in results]
    rps = [r.requests_per_second for r in results]
    
    plt.bar(scenarios, rps)
    plt.xlabel('Scenario')
    plt.ylabel('Requests per Second')
    plt.title('Throughput by Scenario')
    plt.tight_layout()
    plt.savefig(f"{output_dir}/throughput_by_scenario.png")
    plt.close()
    
    # Chart 2: Average response time by scenario
    plt.figure(figsize=(10, 6))
    avg_times = [r.avg_response_time for r in results]
    
    plt.bar(scenarios, avg_times)
    plt.xlabel('Scenario')
    plt.ylabel('Average Response Time (ms)')
    plt.title('Average Response Time by Scenario')
    plt.tight_layout()
    plt.savefig(f"{output_dir}/avg_response_time_by_scenario.png")
    plt.close()
    
    # Chart 3: Response time by endpoint (across all scenarios)
    plt.figure(figsize=(14, 8))
    
    endpoint_names = TEST_ENDPOINTS
    x = np.arange(len(endpoint_names))
    width = 0.25
    
    # Collect data for each scenario
    for i, result in enumerate(results):
        endpoint_avg_times = []
        for endpoint in endpoint_names:
            # Find the stats for this endpoint
            stats = next((s for s in result.endpoint_stats if s.endpoint == endpoint), None)
            endpoint_avg_times.append(stats.avg_response_time if stats else 0)
        
        plt.bar(x + i*width, endpoint_avg_times, width, label=result.scenario_name)
    
    plt.xlabel('Endpoint')
    plt.ylabel('Average Response Time (ms)')
    plt.title('Response Time by Endpoint and Scenario')
    plt.xticks(x + width, [ep.split('?')[0] for ep in endpoint_names], rotation=45, ha='right')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{output_dir}/response_time_by_endpoint.png")
    plt.close()
    
    # Chart 4: CPU usage over time for each scenario
    plt.figure(figsize=(10, 6))
    
    for result in results:
        # Create time axis
        time_points = np.linspace(0, result.duration, len(result.cpu_usage))
        plt.plot(time_points, result.cpu_usage, label=result.scenario_name)
    
    plt.xlabel('Time (seconds)')
    plt.ylabel('CPU Usage (%)')
    plt.title('CPU Usage Over Time')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{output_dir}/cpu_usage_over_time.png")
    plt.close()
    
    # Chart 5: Memory usage over time for each scenario
    plt.figure(figsize=(10, 6))
    
    for result in results:
        # Create time axis
        time_points = np.linspace(0, result.duration, len(result.memory_usage))
        plt.plot(time_points, result.memory_usage, label=result.scenario_name)
    
    plt.xlabel('Time (seconds)')
    plt.ylabel('Memory Usage (%)')
    plt.title('Memory Usage Over Time')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{output_dir}/memory_usage_over_time.png")
    plt.close()
    
    print(f"Charts generated in {output_dir}/ directory")

async def main():
    """Run performance tests with different load scenarios."""
    parser = argparse.ArgumentParser(description="API Performance Testing Tool")
    parser.add_argument("--base-url", default=BASE_URL, help=f"Base URL for API (default: {BASE_URL})")
    parser.add_argument("--duration", type=int, default=TEST_DURATION, help=f"Test duration in seconds (default: {TEST_DURATION})")
    parser.add_argument("--light", type=int, default=LIGHT_LOAD, help=f"Number of users for light load (default: {LIGHT_LOAD})")
    parser.add_argument("--medium", type=int, default=MEDIUM_LOAD, help=f"Number of users for medium load (default: {MEDIUM_LOAD})")
    parser.add_argument("--heavy", type=int, default=HEAVY_LOAD, help=f"Number of users for heavy load (default: {HEAVY_LOAD})")
    parser.add_argument("--charts", action="store_true", help="Generate performance charts")
    parser.add_argument("--output-dir", default="performance_results", help="Directory for output charts")
    
    args = parser.parse_args()
    
    # Create load tester
    tester = APILoadTester(args.base_url, TEST_ENDPOINTS)
    
    # Run scenarios
    results = []
    
    light_result = await tester.run_scenario("Light Load", args.light, args.duration)
    results.append(light_result)
    print_scenario_results(light_result)
    
    medium_result = await tester.run_scenario("Medium Load", args.medium, args.duration)
    results.append(medium_result)
    print_scenario_results(medium_result)
    
    heavy_result = await tester.run_scenario("Heavy Load", args.heavy, args.duration)
    results.append(heavy_result)
    print_scenario_results(heavy_result)
    
    # Generate charts if requested
    if args.charts:
        try:
            generate_charts(results, args.output_dir)
        except Exception as e:
            print(f"Error generating charts: {e}")
    
    # Print summary and recommendations
    print("\n" + "="*80)
    print("PERFORMANCE TEST SUMMARY AND RECOMMENDATIONS")
    print("="*80)
    
    # Overall performance assessment
    light_rps = light_result.requests_per_second
    heavy_rps = heavy_result.requests_per_second
    scalability_ratio = heavy_rps / light_rps if light_rps > 0 else 0
    
    print(f"\nScalability Assessment:")
    print(f"- Light Load RPS: {light_rps:.2f}")
    print(f"- Heavy Load RPS: {heavy_rps:.2f}")
    print(f"- Scale Factor: {scalability_ratio:.2f}x (ideal: {args.heavy/args.light:.2f}x)")
    
    if scalability_ratio < 0.5:
        print("- POOR SCALABILITY: The system doesn't scale well under increased load")
    elif scalability_ratio < 0.8:
        print("- MODERATE SCALABILITY: The system shows some degradation under load")
    else:
        print("- GOOD SCALABILITY: The system scales well with increased load")
    
    # Find slowest endpoints
    all_endpoint_stats = []
    for result in results:
        all_endpoint_stats.extend(result.endpoint_stats)
    
    slow_endpoints = sorted(
        all_endpoint_stats, 
        key=lambda s: s.avg_response_time,
        reverse=True
    )
    
    print("\nSlowest Endpoints:")
    for i, stat in enumerate(slow_endpoints[:3], 1):
        print(f"{i}. {stat.endpoint}: {stat.avg_response_time:.2f} ms average response time")
    
    # Resource utilization analysis
    max_cpu = max(max(r.cpu_usage) for r in results)
    avg_cpu = statistics.mean(statistics.mean(r.cpu_usage) for r in results)
    
    print("\nResource Utilization:")
    print(f"- Maximum CPU Usage: {max_cpu:.2f}%")
    print(f"- Average CPU Usage: {avg_cpu:.2f}%")
    
    if max_cpu > 90:
        print("- WARNING: CPU usage spikes above 90% - potential bottleneck")
    
    # Recommendations
    print("\nRecommendations:")
    
    # Identify endpoints with highest p99/avg ratio (most variable performance)
    variable_endpoints = sorted(
        all_endpoint_stats,
        key=lambda s: s.p99_response_time / s.avg_response_time if s.avg_response_time > 0 else 0,
        reverse=True
    )
    
    if variable_endpoints and variable_endpoints[0].p99_response_time / variable_endpoints[0].avg_response_time > 3:
        print(f"1. Add caching for {variable_endpoints[0].endpoint} to improve performance consistency")
    
    # Check for slow database queries
    knowledge_graph_endpoints = [s for s in all_endpoint_stats if "knowledge-graph" in s.endpoint]
    if knowledge_graph_endpoints and any(s.avg_response_time > 500 for s in knowledge_graph_endpoints):
        print("2. Optimize Neo4j queries in knowledge graph endpoints to reduce response times")
    
    # Check overall throughput
    if heavy_rps < 10:
        print("3. Consider performance tuning of the API server and database connections")
    
    return 0

if __name__ == "__main__":
    asyncio.run(main())