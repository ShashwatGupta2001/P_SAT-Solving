#include<iostream>
#include<fstream>
#include<vector>
using namespace std;

unsigned int numVar, numClause;
vector<vector<int> > clause;
vector<vector<vector<int>*> > posClause, negClause;
vector<int> model, modelStack;

unsigned int nextLiteralIndex, decLvl;

vector<double> posLitActivity, negLitActivity;

unsigned int conflicts, propagation, decisions;

inline unsigned int var(int lit)
{
    return abs(lit);
}

void takeInput(string filename)
{
    //cout<<"began"<<endl;
    ifstream cnf;
    cnf.open(filename);
    //cout<<"opened"<<endl;
    char c;
    cnf.get(c);
    while(c=='c')
    {
        while(c!='\n')
        {
            //cout<<"skipping "<<c<<endl;
            cnf.get(c);
        }
        cnf.get(c);
    }
    string aux; //space is the delimiter
    cnf>>aux;
    cnf>>numVar>>numClause;
    clause.resize(numClause);
    posClause.resize(numVar+1);
    negClause.resize(numVar+1);
    
    for(unsigned int i=0; i<numClause; i++)
    {
        int lit;
        cnf>>lit;
        while(lit!=0)
        {
            clause[i].push_back(lit);
            if(lit>0)
            {
                posClause[var(lit)].push_back((vector<int>*) &clause[i]);
            }
            else
            {
                negClause[var(lit)].push_back((vector<int>*) &clause[i]);    
            }
            cnf>>lit;
        }
    }
    model.resize(numVar+1,-1);
    nextLiteralIndex=0;
    decLvl=0;

    posLitActivity.resize(numVar+1,0);
    negLitActivity.resize(numVar+1,0);
    conflicts=0;
    propagation=0;
    decisions=0;
}

int currValLit(int lit)
{
    if(lit>=0)
    {
        return model[lit];
    }
    else
    {
        if(model[-lit]==-1)
        {
            return -1;
        }
        else
        {
            return 1-model[-lit];
        }
    }
}

void setTrueLit(int lit)
{
    modelStack.push_back(lit);
    if(lit>0)
    {
        model[lit]=1;
    }
    else
    {
        model[-lit]=0;
    }
}

void updLitAct(int lit)
{
    unsigned int index = var(lit);
    if(lit>0)
    {
        posLitActivity[index]+=1;
    }
    else{
        negLitActivity[index]+=1;
    }
}

// Could not figure it out
void updConflictClauseAct(const vector<int>& clause)
{
    conflicts++;
    if((conflicts%100==0)){
        //cout<<"8"<<endl;
        for(unsigned int i=1; i<=numVar; i++){
            posLitActivity[i]/=2;
            negLitActivity[i]/=2;
        }
    }

    for(unsigned int i=0; i<clause.size(); i++){
        updLitAct(clause[i]);
    }
    //cout<<"9"<<endl;
}

bool propGiveConflict()
{
    while (nextLiteralIndex<modelStack.size())
    {
        int litToProp=modelStack[nextLiteralIndex];
        nextLiteralIndex++;
        propagation++;

        vector<vector<int>* > clausestoProp = litToProp>0?negClause[var(litToProp)]:posClause[var(litToProp)];
        for(unsigned int i=0; i<clausestoProp.size(); i++){
            vector<int> clauseP = (vector<int>) *clausestoProp[i];

            bool isSomeLitTrue = false;
            int undefLit = 0;
            int lastUndefLit=0;

            for(unsigned int k=0; !(isSomeLitTrue) && k < clauseP.size(); k++){
                int val = currValLit(clauseP[k]);
                if(val==1){
                    isSomeLitTrue=true;
                }
                else if(val==-1){
                    undefLit++;
                    lastUndefLit=clauseP[k];
                }
            }

            if(!(isSomeLitTrue) && undefLit==0){
                updConflictClauseAct(clauseP);
                return true;
            }
            else if(!(isSomeLitTrue) && undefLit==1){//unit clause
                setTrueLit(lastUndefLit);
            }
        }
    }
    return false;
}

void backtrack()
{
    unsigned int i=modelStack.size()-1;
    int lit=0;
    while(modelStack[i]!=0)
    {
        lit=modelStack[i];
        model[var(lit)]=-1;
        modelStack.pop_back();
        --i;
    }
    modelStack.pop_back();
    --decLvl;
    nextLiteralIndex=modelStack.size();
    setTrueLit(-lit); // we are now setting this to false
}

int getNextDecLit() //selecting the most active variable 
{
    decisions++;
    double maxAct=0;
    int mostActVar=0;
    for(unsigned int i=1; i<=numVar; i++){
        if(model[i]==-1)
        {
            if(posLitActivity[i]>=maxAct){
                maxAct=posLitActivity[i];
                mostActVar=i;
            }
            if(negLitActivity[i]>=maxAct){
                maxAct=negLitActivity[i];
                mostActVar=-i;
            }
        }
    }
    return mostActVar;
}

void chkmodel()
{
    for(unsigned int i=0; i<numClause; i++)
    {
        bool someTrue=false;
        for(unsigned int j=0; !(someTrue) && j<clause[i].size(); j++)
        {
            someTrue = (currValLit(clause[i][j])==1);
        }
        if(!someTrue)
        {
            cout<<"Error!! ";
            for(unsigned int j=0; j<clause[i].size(); j++)
            {
                cout<<clause[i][j]<<" ";
            }
            cout<<endl;
            exit(1);
        }
    }
}

void outSAT(bool sat, vector<int> models)
{
    if(sat)
    {
        chkmodel();
        cout<<"SAT"<<endl;
        cout<<"[";
        for(int i=1; i<models.size(); i++){
            cout<<( (model[i]==0)?(-i):(i) );
            if(i<models.size()-1){
                cout<<" ";
            }
        }
        cout<<"]"<<endl;
        exit(15);
    }
    else{
        cout<<"UNSAT"<<endl;
        exit(5);
    }
}

//Could not understand this part ( below the if (declit==0)
void exeDPLL()
{
    while(true)
    {
        while(propGiveConflict())
        {
            if(decLvl==0)
            {
                outSAT(false, model);
            }
            backtrack();
        }
        int decLit=getNextDecLit();
        if(decLit==0)
        {
            outSAT(true, model);
        }
        modelStack.push_back(0);
        nextLiteralIndex++;
        decLvl++;
        setTrueLit(decLit);
    }
}

void chkUnitClause()
{
    for(unsigned int i=0; i<numClause; i++)
    {
        if(clause[i].size()==1)
        {
            int lit=clause[i][0];
            int val=currValLit(lit);
            if(val==0)
            {
                outSAT(false, model);
            }
            else if(val==-1){
                setTrueLit(lit);
            }
        }
    }
}


int main(int argc, char* argv[])
{
    takeInput(argv[1]);

    chkUnitClause();

    exeDPLL();
    return 0;
}