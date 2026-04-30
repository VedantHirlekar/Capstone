using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace dotnet_app.Models
{
    [Table("employees")]   // 👈 IMPORTANT FIX
    public class Employee
    {
        [Key]
        public long Id { get; set; }

        public string Name { get; set; }

        public string Phone { get; set; }
    }
}