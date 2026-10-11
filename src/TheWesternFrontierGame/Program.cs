using System.Text.Json;
using System.Windows.Forms;
using TheWesternFrontierGame;

static class Program
{
    [STAThread]
    static void Main()
    {
        ApplicationConfiguration.Initialize();
        Application.Run(new MainForm());
    }
}
