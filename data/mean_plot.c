#include <vector>
#include <TFile.h>
#include <TH1.h>
#include <TGraph.h>
#include <TCanvas.h>
#include <iostream>

using namespace std;

void mean_plot(const char* prefix, int NDATA,
               double start, double step)
{
    cout << "Input data  : " << prefix << endl;
    cout << "Number data : " << NDATA << endl;
    cout << "Start       : " << start << endl;
    cout << "Step        : " << step << endl;

    vector<double> x(NDATA);
    vector<double> y(NDATA);
    
    for (int i = 0; i <= NDATA-1; i++) {

        char filename[100];
        sprintf(filename, "%s-%03d.root", prefix, i);

        TFile *file = TFile::Open(filename);
       

        if (!file || file->IsZombie()) {
            cout << "Cannot open: " << filename << endl;
            continue;
        }

        TH1 *h = (TH1*)file->Get("ADC_HIGH_7");

        if (h) {
            x[i] = start + (i) * step;
            y[i] = h->GetMean();

            cout << i << "  "
                 << x[i] << "  "
                 << y[i] << endl;
            delete h;
        }

        file->Close();
        delete file;
        

    }

    cout << "beforeG" << endl;

    TGraph *g = new TGraph(NDATA, x.data(), y.data());
    cout << "beforeF" << endl;

    TCanvas *c = new TCanvas("c", "Mean ADC", 800, 600);
    cout << "Hello" << endl;

    g->SetTitle("Mean ADC;Displacement;Mean ADC");
    cout << "happy" << endl;

    g->SetMarkerStyle(20);
    g->Draw("AP");
    cout << "enjoy" << endl;

}
