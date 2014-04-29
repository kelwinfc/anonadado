#include "anonadado.hpp"

using namespace anonadado;
using namespace std;

instance::instance()
{
    this->d = 0;
}

instance::~instance()
{
    delete this->d;
}

string rapidjson_get_string(const rapidjson::Value& v, string field)
{
    const char* f = field.c_str();
    
    if ( !v.HasMember(f) ||
         !v[f].IsString() )
    {
        exit(-1);
    } else {
        return v[f].GetString();
    }
    
    return "";
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
    
/*
    const rapidjson::Value& features = document["features"];
    if(features.IsArray()){

        for (rapidjson::SizeType i = 0; i < features.Size(); i++){
            const rapidjson::Value& next_feature = features[i];
            const rapidjson::Value& properties = next_feature["properties"];

            if ( properties.IsObject() ){
                const rapidjson::Value& type = properties["type"];

                if ( !type.IsString() )
                    continue;

                // Scene
                if ( strcmp(type.GetString(), "scene") == 0) {
                    this->parse_scene(next_feature);
                }
            }
        }

        for (rapidjson::SizeType i = 0; i < features.Size(); i++){
            const rapidjson::Value& next_feature = features[i];
            const rapidjson::Value& properties = next_feature["properties"];

            if ( properties.IsObject() ){
                const rapidjson::Value& type = properties["type"];

                if ( !type.IsString() )
                    continue;

                if ( strcmp(type.GetString(), "verticals") == 0 ) {
                    //TODO
                } else if ( strcmp(type.GetString(), "markings") == 0 ) {
                    //TODO
                } else if ( strcmp(type.GetString(), "pathologies") == 0 ) {
                    //TODO
                }
            }
        }
    }*/
    
    fclose(pFile);
}
