using Avalonia.Controls;          // ← add
namespace Warwalker.UI;           // ← add
public partial class MainWindow : Window
{
    public MainWindow()
    {
        InitializeComponent();
        DataContext = new MainViewModel();   // ← VS Code no longer complains
    }
}

