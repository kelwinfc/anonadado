#include "anonadado.hpp"

using namespace anonadado;
using namespace std;

/*****************************************************************************
 *                                  Feature                                  *
 *****************************************************************************/

feature::feature()
{
    this->name = "";
    this->type = "";
}

void feature::read(const rapidjson::Value& v)
{
    this->name = rapidjson_get_string(v, "name", "");
    this->type = rapidjson_get_string(v, "type", "");
}

void feature::read(std::string filename)
{
    
}

/******************************* Bool Feature ********************************/

bool_feature::bool_feature()
{
    this->default_value = true;
    this->value = true;
    this->type = "bool";
}

void bool_feature::read(const rapidjson::Value& v)
{
    feature::read(v);
    this->default_value = rapidjson_get_bool(v, "default", true);
    this->value = rapidjson_get_bool(v, "value", true);
}

bool bool_feature::get_value()
{
    return this->value;
}

/****************************** String Feature *******************************/

str_feature::str_feature()
{
    this->default_value = "";
    this->value = "";
    this->type = "string";
}


void str_feature::read(const rapidjson::Value& v)
{
    feature::read(v);
    this->default_value = rapidjson_get_string(v, "default", "");
    this->value = rapidjson_get_string(v, "value", "");
}

string str_feature::get_value()
{
    return this->value;
}

/******************************* Float Feature *******************************/

float_feature::float_feature()
{
    this->default_value = 0.0;
    this->value = 0.0;
    this->type = "float";
}


void float_feature::read(const rapidjson::Value& v)
{
    feature::read(v);
    this->default_value = rapidjson_get_float(v, "default", 0.0);
    this->value = rapidjson_get_float(v, "value", 0.0);
}

float float_feature::get_value()
{
    return this->value;
}

/******************************** Int Feature ********************************/

int_feature::int_feature()
{
    this->default_value = 0;
    this->value = 0;
    this->type = "int";
}


void int_feature::read(const rapidjson::Value& v)
{
    feature::read(v);
    this->default_value = rapidjson_get_int(v, "default", 0);
    this->value = rapidjson_get_int(v, "value", 0);
}

int int_feature::get_value()
{
    return this->value;
}

/****************************** Choice Feature *******************************/

choice_feature::choice_feature()
{
    this->default_value = 0;
    this->value = 0;
    this->type = "choice";
}


void choice_feature::read(const rapidjson::Value& v)
{
    feature::read(v);
    string dv = rapidjson_get_string(v, "default", "");
    string av = rapidjson_get_string(v, "value", "");
    
    this->values.clear();
    if ( v.HasMember("values") && v["values"].IsArray() ){
        const rapidjson::Value& values = v["values"];
        int index = 0;
        for (rapidjson::SizeType i = 0; i < values.Size(); i++){

            const rapidjson::Value& v_json = values[i];
            
            if ( v_json.IsString() ){
                string vs = v_json.GetString();
                this->values.push_back(vs);

                if ( vs == dv ){
                    this->default_value = index;
                }
                if ( vs == av ){
                    this->value = index;
                }

                index++;
            }
        }
    }
    
}

string choice_feature::get_value()
{
    return this->values[this->value];
}

/*****************************************************************************/

feature* get_feature(const rapidjson::Value& v)
{
    feature* ret;
    
    string type = rapidjson_get_string(v, "type", "");
    
    if ( type == "bool" ){
        ret = new bool_feature();
    } else if ( type == "string" ){
        ret = new str_feature();
    } else if ( type == "float" ){
        ret = new float_feature();
    } else if ( type == "int" ){
        ret = new int_feature();
    } else if ( type == "choice" ){
        ret = new choice_feature();
    } else {
        ret = new feature();
    }
    
    return ret;
}

/*****************************************************************************
 *                                  Domain                                   *
 *****************************************************************************/

domain::domain()
{
    this->name = "";
}

void domain::read(string filename)
{
    FILE * pFile = fopen (filename.c_str() , "r");
    rapidjson::FileStream is(pFile);
    rapidjson::Document document;
    document.ParseStream<0>(is);
    
    this->clear_labels();

    this->name = rapidjson_get_string(document, "name", "");

    if ( document.HasMember("labels") && document["labels"].IsArray() ){
        const rapidjson::Value& labels = document["labels"];
        for (rapidjson::SizeType i = 0; i < labels.Size(); i++){
            const rapidjson::Value& a_json = labels[i];
            annotation* a = new annotation();
            a->read(a_json);
            
            this->labels[a->get_name()] = a;
        }
    }
    
    fclose(pFile);
}

annotation* domain::get_instance(string label_name)
{
    annotation* ret = 0;

    if ( this->labels.find(label_name) != this->labels.end() ){
        
    }
    return ret;
}

void domain::clear_labels()
{
    map<string, annotation*>::iterator it;

    for ( it = this->labels.begin(); it != this->labels.end(); ++it ){
        delete it->second;
    }
}

/*****************************************************************************
 *                                Annotation                                 *
 *****************************************************************************/

annotation::annotation()
{
    this->frame = -1;
    this->is_unique = false;
    this->is_global = false;
    this->name = "";
}

annotation::~annotation()
{
    this->clear_features();
}

void annotation::read(const rapidjson::Value& v)
{
    this->frame = rapidjson_get_int(v, "frame", -1);
    this->is_unique = rapidjson_get_bool(v, "is_unique", false);
    this->is_global = rapidjson_get_bool(v, "is_global", false);
    this->name = rapidjson_get_string(v, "name", "");
    
    this->clear_features();
    if ( v.HasMember("features") && v["features"].IsArray() )
    {
        const rapidjson::Value& f = v["features"];
        
        for (rapidjson::SizeType i = 0; i < f.Size(); i++){
            const rapidjson::Value& f_json = f[i];
            feature* f = get_feature(f_json);
            this->features.push_back(f);
        }
    }
}

void annotation::read(std::string filename)
{
    FILE * pFile = fopen (filename.c_str() , "r");
    rapidjson::FileStream is(pFile);
    rapidjson::Document document;
    document.ParseStream<0>(is);

    this->read(document);
    
    fclose(pFile);
}

string annotation::get_name()
{
    return this->name;
}

void annotation::clear_features()
{
    vector<feature*>::iterator it;
    for ( it = this->features.begin(); it != this->features.end(); ++it){
        delete *it;
    }
}

/*****************************************************************************
 *                                 Instance                                  *
 *****************************************************************************/

instance::instance()
{
    this->d = 0;
}

instance::~instance()
{
    if ( this->d ){
        delete this->d;
    }
    
    this->clear_annotations();
}

void instance::read(string filename)
{
    FILE * pFile = fopen (filename.c_str() , "r");
    rapidjson::FileStream is(pFile);
    rapidjson::Document document;
    document.ParseStream<0>(is);

    this->sequence_filename =
        rapidjson_get_string(document, "sequence_filename");

    this->video_filename =
        rapidjson_get_string(document, "video_filename");
    
    this->instance_name = rapidjson_get_string(document, "name");
    this->instance_filename = filename;

    this->domain_filename = rapidjson_get_string(document, "domain");

    if ( this->d != 0 ){
        delete this->d;
    }
    
    this->d = new domain();
    this->d->read(this->domain_filename);

    this->clear_annotations();
    if ( document.HasMember("sequence") && document["sequence"].IsArray() )
    {
        const rapidjson::Value& sequence = document["sequence"];

        for (rapidjson::SizeType i = 0; i < sequence.Size(); i++){
            const rapidjson::Value& n_annotation = sequence[i];

            vector<annotation*> next;

            if ( n_annotation.IsArray() ){
                for (rapidjson::SizeType j = 0; j < n_annotation.Size(); j++){
                    const rapidjson::Value& nn_annotation = n_annotation[j];
                    annotation* n = new annotation();
                    //n->read(nn_annotation);
                    
                    next.push_back(n);
                }
            }

            this->annotations.push_back(next);
        }
    }
    
    fclose(pFile);
}

void instance::clear_annotations()
{
    vector< vector<annotation*> >::iterator it;
    for ( it = this->annotations.begin(); it != this->annotations.end(); ++it){
        vector<annotation*>::iterator inner_it;
        for ( inner_it = it->begin(); inner_it != it->end(); ++inner_it){
            delete *inner_it;
        }
    }
}