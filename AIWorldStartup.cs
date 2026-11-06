using System;
using System.Diagnostics;

public static class AIWorldStartup
{
    public static void Main(string[] args)
    {
        var host = Environment.GetEnvironmentVariable("AIWORLD_HOST") ?? "http://localhost";
        var universalPort = Environment.GetEnvironmentVariable("UNIVERSAL_API_PORT") ?? "8080";
        var universalUrl = $"{host.TrimEnd('/')}:{universalPort}";

        Console.WriteLine("AI World - NetworkBuster");
        Console.WriteLine($"Launching: {universalUrl}");

        try
        {
            Process.Start(new ProcessStartInfo
            {
                FileName = universalUrl,
                UseShellExecute = true
            });
        }
        catch (Exception ex)
        {
            Console.WriteLine("Could not open the browser automatically.");
            Console.WriteLine($"Open this URL manually: {universalUrl}");
            Console.WriteLine(ex.Message);
        }
    }
}
