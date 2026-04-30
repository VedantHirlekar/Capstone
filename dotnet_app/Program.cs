using dotnet_app.Data;
using Microsoft.EntityFrameworkCore;

var builder = WebApplication.CreateBuilder(args);

// ==========================
// 1. Controllers
// ==========================
builder.Services.AddControllers();

// ==========================
// 2. ENV VARIABLES (DOCKER READY)
// ==========================
var dbHost = Environment.GetEnvironmentVariable("DB_HOST");
var dbUser = Environment.GetEnvironmentVariable("DB_USER");
var dbPass = Environment.GetEnvironmentVariable("DB_PASSWORD");
var dbName = Environment.GetEnvironmentVariable("DB_NAME");
var dbPort = Environment.GetEnvironmentVariable("DB_PORT") ?? "3306";

var connectionString =
    $"server={dbHost};port={dbPort};database={dbName};user={dbUser};password={dbPass}";

// ==========================
// 3. DbContext
// ==========================
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseMySql(
        connectionString,
        new MySqlServerVersion(new Version(8, 0, 36))
    )
);

// ==========================
// 4. CORS
// ==========================
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowFrontend",
        policy =>
        {
            policy.WithOrigins("http://localhost:3000")
                  .AllowAnyHeader()
                  .AllowAnyMethod();
        });
});

var app = builder.Build();

// ==========================
// 5. Middleware order (IMPORTANT)
// ==========================
app.UseCors("AllowFrontend");

app.UseAuthorization();

app.MapControllers();

app.Run();