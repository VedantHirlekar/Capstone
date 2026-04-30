using Microsoft.AspNetCore.Mvc;
using dotnet_app.Data;
using dotnet_app.Models;

namespace dotnet_app.Controllers;

[ApiController]
[Route("employees")]
public class EmployeeController : ControllerBase
{
    private readonly AppDbContext _context;

    public EmployeeController(AppDbContext context)
    {
        _context = context;
    }

    // 🔥 GET
    [HttpGet]
    public IEnumerable<Employee> Get()
    {
        var start = DateTime.Now;

        Console.WriteLine($"🔥 DOTNET HIT → GET /employees");

        var data = _context.Employees.ToList();

        Console.WriteLine($"✅ DOTNET RESPONSE → GET /employees | 200 | {(DateTime.Now - start).TotalMilliseconds}ms");

        return data;
    }

    // 🔥 POST
    [HttpPost]
    public Employee Post([FromBody] Employee emp)
    {
        var start = DateTime.Now;

        Console.WriteLine($"🔥 DOTNET HIT → POST /employees");
        Console.WriteLine($"📦 Body: name={emp.Name}, phone={emp.Phone}");

        _context.Employees.Add(emp);
        _context.SaveChanges();

        Console.WriteLine($"✅ DOTNET RESPONSE → POST /employees | 200 | {(DateTime.Now - start).TotalMilliseconds}ms");

        return emp;
    }
}