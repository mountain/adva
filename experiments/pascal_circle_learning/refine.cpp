// Original bounded numerical proposer by ChatGPT (OpenAI), through Mingli Yuan.
// Contributed under Unknown v0.3. Floating scores never authorize acceptance.
#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <complex>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <random>
#include <string>
#include <vector>
using namespace std;
constexpr double PI = 3.141592653589793238462643383279502884;
struct P {
    double x, y;
    P operator+(P b) const { return {x+b.x,y+b.y}; }
    P operator-(P b) const { return {x-b.x,y-b.y}; }
    P operator*(double s) const { return {x*s,y*s}; }
};
double cr(P a,P b) { return a.x*b.y-a.y*b.x; }
double dot(P a,P b) { return a.x*b.x+a.y*b.y; }
double norm(P a) { return sqrt(dot(a,a)); }
P meet(P a,P b,P c,P d) {
    P u=b-a,v=d-c;
    double w=cr(u,v);
    if(abs(w)<1e-9) return {1e20,1e20};
    return a+u*(cr(c-a,v)/w);
}
P tanmeet(P a,P b) {
    double z=cr(a,b);
    if(abs(z)<1e-9) return {1e20,1e20};
    return {(b.y-a.y)/z,(a.x-b.x)/z};
}
P tanline(P a,P b,P c) { return meet(a,a+P{-a.y,a.x},b,c); }
using V = array<double,7>;
using Z = complex<double>;
array<P,14> target;
struct Sim { double a,b,cx,cy; };
bool finite(Z z) { return isfinite(z.real()) && isfinite(z.imag()); }
array<P,14> raw(V x) {
    array<P,14> p{};
    P r[5],b[4];
    double ra[5]={0,x[0],x[1],x[2],x[0]-x[2]};
    double ba[4]={0,x[3],x[4],x[5]};
    for(int i=0;i<5;i++) r[i]={cos(ra[i]),sin(ra[i])};
    for(int i=0;i<4;i++) b[i]={cos(ba[i]),sin(ba[i])};
    int ri[5]={1,3,5,7,9};
    for(int i=0;i<5;i++) p[ri[i]]=r[i];
    p[11]=tanline(r[0],r[2],r[3]);
    p[13]=meet(r[1],r[2],r[4],r[0]);
    int bi[4]={2,4,8,12};
    for(int i=0;i<4;i++) p[bi[i]]=b[i];
    p[0]=tanmeet(b[0],b[2]);
    p[6]=meet(b[0],b[1],b[2],b[3]);
    p[10]=meet(b[1],b[2],b[3],b[0]);
    return p;
}
// Complex least squares for red C+q*r and blue C+q*k+s*b, |k|=1.
// Thus the blue center lies on the red circle by construction. Solve the
// 3x3 Hermitian normal system with partial pivoting; singular fits are refused.
bool jointfit(array<P,14>& p,double direction,array<Sim,2>& out) {
    Z k=polar(1.0,direction), matrix[3][4]{};
    for(int i=0;i<14;i++) {
        Z z(p[i].x,p[i].y), t(target[i].x,target[i].y);
        array<Z,3> row = (i%2) ? array<Z,3>{1.0,z,0.0}
                                     : array<Z,3>{1.0,k,z};
        for(int a=0;a<3;a++) {
            for(int b=0;b<3;b++) matrix[a][b]+=conj(row[a])*row[b];
            matrix[a][3]+=conj(row[a])*t;
        }
    }
    double scale=0;
    for(int a=0;a<3;a++) for(int b=0;b<3;b++) {
        if(!finite(matrix[a][b])) return false;
        scale=max(scale,abs(matrix[a][b]));
    }
    for(int col=0;col<3;col++) {
        int pivot=col;
        for(int a=col+1;a<3;a++)
            if(abs(matrix[a][col])>abs(matrix[pivot][col])) pivot=a;
        if(abs(matrix[pivot][col])<=1e-12*max(1.0,scale)) return false;
        if(pivot!=col) for(int b=col;b<4;b++) swap(matrix[col][b],matrix[pivot][b]);
        Z diagonal=matrix[col][col];
        for(int b=col;b<4;b++) matrix[col][b]/=diagonal;
        for(int a=0;a<3;a++) if(a!=col) {
            Z factor=matrix[a][col];
            for(int b=col;b<4;b++) matrix[a][b]-=factor*matrix[col][b];
        }
    }
    Z c=matrix[0][3],q=matrix[1][3],s=matrix[2][3],cb=c+q*k;
    if(!finite(c)||!finite(q)||!finite(s)||!finite(cb)||abs(q)<=1e-9||abs(s)<=1e-9)
        return false;
    out={Sim{q.real(),q.imag(),c.real(),c.imag()},
         Sim{s.real(),s.imag(),cb.real(),cb.imag()}};
    for(int i=0;i<14;i++) {
        Z z(p[i].x,p[i].y), fitted=(i%2)?c+q*z:cb+s*z;
        if(!finite(fitted)) return false;
        p[i]={fitted.real(),fitted.imag()};
    }
    return true;
}
struct Score { double loss,mse; int crossings; };
Score evaluate(V x,array<Sim,2>* out=nullptr) {
    for(double z:x) if(!isfinite(z)) return {1000,1000,99};
    auto p=raw(x);
    for(P z:p) if(!isfinite(z.x)||!isfinite(z.y)||norm(z)>1e7)
        return {1000,1000,99};
    array<Sim,2> fits{};
    if(!jointfit(p,x[6],fits)) return {1000,1000,99};
    if(out) *out=fits;
    double mse=0;
    for(int i=0;i<14;i++) mse+=dot(p[i]-target[i],p[i]-target[i])/14;
    if(!isfinite(mse)) return {1000,1000,99};
    double mingap=1e99;
    for(int i=0;i<14;i++) for(int j=i+1;j<14;j++)
        mingap=min(mingap,norm(p[i]-p[j]));
    if(mingap<=.005) return {100+mse,mse,99};
    int n=0;
    double pen=0;
    for(int i=0;i<14;i++) for(int j=i+2;j<14;j++) {
        if(i==0&&j==13) continue;
        P a=p[i],b=p[(i+1)%14],c=p[j],d=p[(j+1)%14];
        double ab=norm(b-a),cd=norm(d-c);
        double d1=cr(b-a,c-a)/ab,d2=cr(b-a,d-a)/ab;
        double d3=cr(d-c,a-c)/cd,d4=cr(d-c,b-c)/cd;
        if(!isfinite(d1)||!isfinite(d2)||!isfinite(d3)||!isfinite(d4))
            return {1000,1000,99};
        if(d1*d2<=1e-14&&d3*d4<=1e-14) {
            n++;
            pen+=min(min(abs(d1),abs(d2)),min(abs(d3),abs(d4)));
        }
    }
    double loss=mse+.15*n+pen;
    if(!isfinite(loss)) return {1000,1000,99};
    return {loss,mse,n};
}
int main(int argc,char** argv) {
    auto start=chrono::steady_clock::now();
    if(argc!=3) return 3;
    ifstream in(argv[1]);
    // Exactly 28 target scalars followed by two seven-angle starting points.
    for(auto& z:target) in>>z.x>>z.y;
    V generic{},source{};
    for(auto& z:generic) in>>z;
    for(auto& z:source) in>>z;
    if(!in) return 4;
    for(P z:target) if(!isfinite(z.x)||!isfinite(z.y)) return 4;
    for(double z:generic) if(!isfinite(z)) return 4;
    for(double z:source) if(!isfinite(z)) return 4;
    string extra;
    if(in>>extra) return 4;
    mt19937_64 rng(172902);
    normal_distribution<double> N(0,1);
    uniform_real_distribution<double> U(0,1);
    int evals=0;
    double global=1e99,bestmse=1e99;
    V gx=generic,bx=generic;
    vector<pair<double,V>> records;
    auto seconds=[&]() { return chrono::duration<double>(chrono::steady_clock::now()-start).count(); };
    auto retain=[&](V x,Score s,int restart) {
        if(s.loss<global) { global=s.loss; gx=x; }
        if(s.crossings==0&&s.mse<bestmse) {
            bestmse=s.mse; bx=x; records.push_back({bestmse,bx});
            cerr<<"best_rms "<<sqrt(bestmse)<<" evals "<<evals
                <<" restart "<<restart<<" seconds "<<seconds()<<" angles";
            for(double v:bx) cerr<<" "<<setprecision(17)<<v;
            cerr<<"\n";
        }
    };
    auto write=[&](const string& reason) {
        ofstream f(argv[2]);
        if(!f) return false;
        bool feasible=bestmse<1e98&&isfinite(bestmse);
        f<<setprecision(17)<<"{\"status\":\""<<(reason.empty()?"Proposed":"Unknown")
            <<"\",\"evaluations\":"<<evals;
        if(!reason.empty()) f<<",\"reason\":\""<<reason<<"\"";
        if(feasible) {
            f<<",\"best_rms\":"<<sqrt(bestmse)<<",\"angles\":[";
            for(int z=0;z<7;z++) f<<(z?",":"")<<bx[z];
            f<<"]";
        }
        f<<",\"records\":[";
        int from=max(0,(int)records.size()-20);
        for(int i=from;i<(int)records.size();i++) {
            f<<(i>from?",":"")<<"{\"mse\":"<<records[i].first<<",\"angles\":[";
            for(int z=0;z<7;z++) f<<(z?",":"")<<records[i].second[z];
            f<<"]}";
        }
        f<<"]}\n";
        return bool(f);
    };
    for(int restart=0;restart<12;restart++) {
        V x{};
        if(restart==0) x=source;
        else if(restart==1) x=generic;
        else if(restart%3==0) for(double& z:x) z=(U(rng)*2-1)*PI;
        else if(bestmse<1e98) {
            x=bx;
            for(double& z:x) z+=N(rng)*(restart%3==1?.6:1.7);
        } else {
            x=gx;
            for(double& z:x) z+=N(rng)*1.2;
        }
        Score s=evaluate(x);
        evals++;
        retain(x,s,restart);
        cerr<<"initial restart "<<restart<<" eval "<<evals<<" rms "
            <<sqrt(s.mse)<<" crossings "<<s.crossings<<"\n";
        for(int it=0;it<4000;it++) {
            if(seconds()>165) {
                if(!write("search-wall-time-limit")) return 5;
                cout<<"UNKNOWN time evals="<<evals<<"\n";
                return 2;
            }
            double phase=double(it)/4000;
            double temp=.13*pow(.00003/.13,phase);
            V y=x;
            int k=rng()%7;
            double sig=.6*pow(.001/.6,phase);
            y[k]+=N(rng)*sig;
            if(U(rng)<.07) for(double& z:y) z+=N(rng)*sig;
            auto t=evaluate(y);
            evals++;
            retain(y,t,restart);
            if(t.loss<s.loss||U(rng)<exp((s.loss-t.loss)/temp)) { x=y; s=t; }
        }
    }
    if(bestmse>=1e98||!isfinite(bestmse)) {
        if(!write("no-feasible-numerical-candidate")) return 5;
        cout<<"UNKNOWN no-feasible-numerical-candidate evals="<<evals<<"\n";
        return 1;
    }
    if(!write("")) return 5;
    cout<<"evals="<<evals<<" best_rms="<<sqrt(bestmse)<<"\n";
    return 0;
}
