using Avalonia.Controls;
using System.Diagnostics;
using System.Threading.Tasks;
using Avalonia.Media;
using System.IO;
using System;
using System.Runtime.CompilerServices;
using System.Linq;


namespace worldMinerUI;

public partial class MainWindow : Window
{

    private Process? minerProcess;

    private bool isRunning = false;
    private bool isFirstLine = true;


    public MainWindow()
    {
        InitializeComponent();

        StartStopButton.Click += OnStartStopClick;

        // Task.Run(() => parallelGetLastLine());

        Box1.Text = "Restants";
        Box2.Text = "Temps Et";
        Box3.Text = "Poids Et";
        Box4.Text = "Traités";
        Box5.Text = "Rc JSON";
        Box6.Text = "Rc PUUID";
        Box7.Text = "Nettoyage";
        Box8.Text = "Save";
        Box11.Text = "Bloc Total";

        IndicatorStep1.Fill = Brushes.Red;
        IndicatorStep2.Fill = Brushes.Red;

    }


    private void writeOnTextBox(string text, bool firstLine = false)
    {
        if (LogBox != null)
        {
            Avalonia.Threading.Dispatcher.UIThread.Post(() =>
            {
                if (!firstLine)
                {
                    LogBox.Text += Environment.NewLine;
                    LogBox.Text += text;
                }
                else
                {
                    LogBox.Text = text;
                }
            });
        }
    }


    /*private int getCurrentSpeed()


    private void parallelGetLastLine()
    {
        while (true)
        {
            System.Threading.Thread.Sleep(50);
            Avalonia.Threading.Dispatcher.UIThread.Post(() =>
            {
                string lastLine = LogBox.Text?.Split([Environment.NewLine], StringSplitOptions.None).LastOrDefault() ?? string.Empty;
                LogBox2.Text = lastLine;
            });
        }
    }*/


    private void handlePythonOutput(string line)
    {

        // writeOnTextBox(line);

        if (LogBox != null)
        {
            // Affiche la ligne
            // writeOnTextBox(line);

            // Ici tu peux ajouter ton analyse personnalisée :
            if (line.StartsWith("MR:"))
            {
                // writeOnTextBox(line.Substring(3));
                Avalonia.Threading.Dispatcher.UIThread.Post(() =>
                {
                    Box100.Text = line.Substring(3);
                });
            }
            else if (line.StartsWith("TR:"))
            {
                // writeOnTextBox(line.Substring(3));
                Avalonia.Threading.Dispatcher.UIThread.Post(() =>
                {
                    Box200.Text = line.Substring(3);
                });
            }
            else if (line.StartsWith("PR:"))
            {
                // writeOnTextBox(line.Substring(3));
                Avalonia.Threading.Dispatcher.UIThread.Post(() =>
                {
                    Box300.Text = line.Substring(3);
                });
            }
            // else if (line.StartsWith("NM:"))
            // {
            //     // writeOnTextBox(line.Substring(3));
            //     Avalonia.Threading.Dispatcher.UIThread.Post(() =>
            //     {
            //         Box400.Text = line.Substring(3);
            //         IndicatorStep3.Fill = Brushes.Blue;
            //         LogBox2.Text = "";
            //     });
            // }
            else if (line.StartsWith("MT:"))
            {
                // writeOnTextBox(line.Substring(3));
                Avalonia.Threading.Dispatcher.UIThread.Post(() =>
                {
                    Box400.Text = line.Substring(3);
                    IndicatorStep3.Fill = Brushes.Blue;
                    LogBox2.Text = "";
                });
            }
            else if (line.StartsWith("TM:"))
            {
                // writeOnTextBox(line.Substring(3));
                Avalonia.Threading.Dispatcher.UIThread.Post(() =>
                {
                    Box500.Text = line.Substring(3);
                });
            }
            else if (line.StartsWith("TP:"))
            {
                // writeOnTextBox(line.Substring(3));
                Avalonia.Threading.Dispatcher.UIThread.Post(() =>
                {
                    Box600.Text = line.Substring(3);
                });
            }
            else if (line.StartsWith("NJ:"))
            {
                // writeOnTextBox(line.Substring(3));
                Avalonia.Threading.Dispatcher.UIThread.Post(() =>
                {
                    Box700.Text = line.Substring(3);
                });
            }
            else if (line.StartsWith("SJ:"))
            {
                // writeOnTextBox(line.Substring(3));
                Avalonia.Threading.Dispatcher.UIThread.Post(() =>
                {
                    Box800.Text = line.Substring(3);
                });
            }
            // else if (line.StartsWith("BJ:"))
            // {
            //     // writeOnTextBox(line.Substring(3));
            //     Avalonia.Threading.Dispatcher.UIThread.Post(() =>
            //     {
            //         Box900.Text = line.Substring(3);
            //     });
            // }
            // else if (line.StartsWith("BP:"))
            // {
            //     // writeOnTextBox(line.Substring(3));
            //     Avalonia.Threading.Dispatcher.UIThread.Post(() =>
            //     {
            //         Box1000.Text = line.Substring(3);
            //     });
            // }
            else if (line.StartsWith("TB:"))
            {
                // writeOnTextBox(line.Substring(3));
                Avalonia.Threading.Dispatcher.UIThread.Post(() =>
                {
                    Box1100.Text = line.Substring(3);
                });
            }
            else if (line.StartsWith("ID:"))
            {
                Avalonia.Threading.Dispatcher.UIThread.Post(() =>
                {
                    if (isFirstLine)
                    {
                        writeOnTextBox(line.Substring(3), firstLine: true);
                        isFirstLine = false;
                    }
                    else
                    {
                        writeOnTextBox(line.Substring(3));
                    }
                });
            }
            else if (line.StartsWith("SP:"))
            {
                Avalonia.Threading.Dispatcher.UIThread.Post(() =>
                {
                    float speed = float.Parse(line.Substring(3), System.Globalization.CultureInfo.InvariantCulture);
                    if (speed < 1) IndicatorStep4.Fill = Brushes.Red;
                    else if (speed < 3) IndicatorStep4.Fill = Brushes.OrangeRed;
                    else if (speed < 5) IndicatorStep4.Fill = Brushes.Orange;
                    else if (speed < 6) IndicatorStep4.Fill = Brushes.Yellow;
                    else if (speed < 8) IndicatorStep4.Fill = Brushes.Green;
                    else if (speed < 10) IndicatorStep4.Fill = Brushes.LimeGreen;
                    else IndicatorStep4.Fill = Brushes.White;
                    IndicatorStep5TextBox.Text = speed.ToString("F2", System.Globalization.CultureInfo.InvariantCulture) + " H/s";
                });
            }



            else if (line.StartsWith("ELC"))
            {
                Avalonia.Threading.Dispatcher.UIThread.Post(() =>
                {
                    IndicatorStep1.Fill = Brushes.Red;
                    IndicatorStep2.Fill = Brushes.Red;
                    IndicatorStep3.Fill = Brushes.Red;
                    IndicatorStep4.Fill = Brushes.Red;
                    IndicatorStep5TextBox.Text = "0 H/s";
                    LogBox2.Text = "[ERREUR] Vérifie que LoL est lancé et connecté. On réessaie.";
                });
            }
            else if (line.StartsWith("VLC"))
            {
                Avalonia.Threading.Dispatcher.UIThread.Post(() =>
                {
                    IndicatorStep1.Fill = Brushes.Blue;
                    IndicatorStep2.Fill = Brushes.Orange;
                    LogBox2.Text = "Requête au LCU.";
                });
                // writeOnTextBox("[VALIDE] LCU connecté.");
            }
            else if (line.StartsWith("ERL"))
            {
                Avalonia.Threading.Dispatcher.UIThread.Post(() =>
                {
                    IndicatorStep2.Fill = Brushes.Red;
                    LogBox2.Text = "[ERREUR] Aucun accès au token. LoL doit être connecté.";
                });
            }
            else if (line.StartsWith("VRL"))
            {
                Avalonia.Threading.Dispatcher.UIThread.Post(() =>
                {
                    IndicatorStep2.Fill = Brushes.Blue;
                    IndicatorStep3.Fill = Brushes.Orange;
                    LogBox2.Text = "Qualité des Matchs.";
                });
                // writeOnTextBox("[VALIDE] Token récupéré.");
            }
            else if (line.StartsWith("ESG"))
            {
                Avalonia.Threading.Dispatcher.UIThread.Post(() =>
                {
                    IndicatorStep3.Fill = Brushes.Red;
                    LogBox2.Text = "[ERREUR] Structure inattendue de la clé 'games'..(?) On passe le PUUID.";
                });
            }
            else if (line.StartsWith("EP:"))
            {
                Avalonia.Threading.Dispatcher.UIThread.Post(() =>
                {
                    IndicatorStep0.Fill = Brushes.Blue;
                    IndicatorStep1.Fill = Brushes.Orange;
                    LogBox2.Text = "Connexion au LCU.";
                });
            }
        }
    }




    private void OnStartStopClick(object? sender, Avalonia.Interactivity.RoutedEventArgs e)
    {


        var motherDirectory = Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, "..", "..", "..", ".."));

        if (!isRunning)
        {
            Avalonia.Threading.Dispatcher.UIThread.Post(() =>
            {
                LogBox2.Text = "Démarrage.";
            });
            // Démarrer le process Python
            minerProcess = new Process
            {
                StartInfo = new ProcessStartInfo
                {
                    FileName = "python",
                    Arguments = "-u worldMiner.py",
                    WorkingDirectory = motherDirectory,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = true
                }
            };

            minerProcess.OutputDataReceived += (s, args) =>
            {
                if (!string.IsNullOrEmpty(args.Data))
                {
                    // writeOnTextBox(args.Data);
                    handlePythonOutput(args.Data!);
                }
            };
            minerProcess.ErrorDataReceived += (s, args) =>
            {
                if (!string.IsNullOrEmpty(args.Data))
                {
                    writeOnTextBox("[ERREUR] " + args.Data);
                    Avalonia.Threading.Dispatcher.UIThread.Post(() =>
                    {
                        LogBox2.Text = args.Data;
                    });
                    OnStartStopClick(this, e);
                }
            };

            minerProcess.Start();
            minerProcess.BeginOutputReadLine();
            minerProcess.BeginErrorReadLine();

            Avalonia.Threading.Dispatcher.UIThread.Post(() =>
            {
                LogBox.CaretIndex = int.MaxValue;
                StartStopButton.Content = "Arrêter";

                isRunning = true;

                // Indicateur en cours (vert)
                IndicatorStep0.Fill = Brushes.Orange; // Change à "En cours"
                LogBox2.Text = "Récupération des PUUIDs.";
            });

        }
        else
        {
            Avalonia.Threading.Dispatcher.UIThread.Post(() =>
            {
                LogBox2.Text = "Arrêt.";
            });

            // Arrêter le process Python
            if (minerProcess != null && !minerProcess.HasExited)
            {
                minerProcess.Kill(true);
                minerProcess = null;
            }
            isRunning = false;

            Avalonia.Threading.Dispatcher.UIThread.Post(() =>
            {
                StartStopButton.Content = "Lancer";
            
                IndicatorStep0.Fill = Brushes.Red;
                IndicatorStep1.Fill = Brushes.Red;
                IndicatorStep2.Fill = Brushes.Red;
                IndicatorStep3.Fill = Brushes.Red;
                IndicatorStep4.Fill = Brushes.Red;
            });
        }
    }
}