void check_vmppc(std::string filename="../data/summer024.root"){// 1. ファイルを開く
    TFile *f = TFile::Open(filename.c_str());
    
    // 2. ヒストグラムを取得
    TH1 *h = (TH1*)f->Get("ADC_HIGH_7");
    
    // 3. キャンバスを作成して描画
    TCanvas *c1 = new TCanvas("c1", "ADC_HIGH_7 Canvas", 800, 600);
    h->Draw();
    h->Fit("gaus","R","same",780,830);
    h->Fit("gaus","R+","same",840,870);
    h->Fit("gaus","R+","same",880,920);
    h->Fit("gaus","R+","same",930,960);
}
