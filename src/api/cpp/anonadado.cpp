#include "anonadado.hpp"

using namespace anonadado;
using namespace std;

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
    vector<feature*>::iterator it, end;
    end = this->features.end();
    
    for ( it = this->features.begin(); it != end; ++it ){
        delete *it;
    }
}

void annotation::read(const rapidjson::Value& v)
{
    this->frame = rapidjson_get_int(v, "frame", -1);
    this->is_unique = rapidjson_get_bool(v, "is_unique", false);
    this->is_global = rapidjson_get_bool(v, "is_global", false);
    this->name = rapidjson_get_string(v, "name", "");

    // TODO: parse features
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

/*****************************************************************************
 *                                 Instance                                  *
 *****************************************************************************/

instance::instance()
{
    this->d = 0;
}

instance::~instance()
{
    delete this->d;
}

void instance::read(string filename)
{
    /*
        domain* d;
        std::vector<annotation*> annotations;
    */
    
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
    this->d = new domain();
    
    // TODO: parse domain
    
    fclose(pFile);
}
