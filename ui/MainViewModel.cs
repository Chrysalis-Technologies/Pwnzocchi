using System.Collections.ObjectModel;
using ReactiveUI;

namespace Warwalker.UI;

public sealed class MainViewModel : ReactiveObject
{
    private readonly ObservableCollection<HandshakeRecord> _handshakes = new();
    public ReadOnlyObservableCollection<HandshakeRecord> Handshakes { get; }

    private string _status = "Idle";
    public string Status
    {
        get => _status;
        set => this.RaiseAndSetIfChanged(ref _status, value);
    }

    public MainViewModel()
    {
        Handshakes = new(_handshakes);   // wrap in read-only view
    }
}

public record HandshakeRecord(string Ssid, string Mac, string State);
