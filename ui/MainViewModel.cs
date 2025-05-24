using System.Collections.ObjectModel;
using ReactiveUI;
using System.Diagnostics;
using System.Reactive;
using System.Threading.Tasks;

namespace Warwalker.UI;

public sealed class MainViewModel : ReactiveObject
{
    private readonly ObservableCollection<HandshakeRecord> _handshakes = new();
    public ReadOnlyObservableCollection<HandshakeRecord> Handshakes { get; }

    public ReactiveCommand<Unit, Unit> StartScan { get; }

    private string _status = "Idle";
    public string Status
    {
        get => _status;
        set => this.RaiseAndSetIfChanged(ref _status, value);
    }

    public MainViewModel()
    {
        Handshakes = new(_handshakes);   // wrap in read-only view

        StartScan = ReactiveCommand.CreateFromTask(StartScanAsync);
    }

    private async Task StartScanAsync()
    {
        Status = "Scanning...";

        var psi = new ProcessStartInfo
        {
            FileName = "python3",
            Arguments = "core/main.py",
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
            CreateNoWindow = true
        };

        using var process = new Process { StartInfo = psi };

        process.OutputDataReceived += (_, e) =>
        {
            if (!string.IsNullOrWhiteSpace(e.Data))
            {
                Status = e.Data;
            }
        };

        process.ErrorDataReceived += (_, e) =>
        {
            if (!string.IsNullOrWhiteSpace(e.Data))
            {
                Status = e.Data;
            }
        };

        process.Start();
        process.BeginOutputReadLine();
        process.BeginErrorReadLine();
        await process.WaitForExitAsync();

        Status = "Done";
    }
}

public record HandshakeRecord(string Ssid, string Mac, string State);
