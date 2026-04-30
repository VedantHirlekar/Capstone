using Microsoft.EntityFrameworkCore;
using dotnet_app.Models;

namespace dotnet_app.Data;

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) {}

    public DbSet<Employee> Employees { get; set; }
}