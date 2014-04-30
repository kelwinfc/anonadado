#include "utils.hpp"

string rapidjson_get_string(const rapidjson::Value& v, string field,
                            string default_value)
{
    const char* f = field.c_str();

    if ( !v.HasMember(f) || !v[f].IsString() )
    {
        return default_value;
    } else {
        return v[f].GetString();
    }
}

int rapidjson_get_int(const rapidjson::Value& v, string field,
                      int default_value)
{
    const char* f = field.c_str();

    if ( !v.HasMember(f) || !v[f].IsInt() )
    {
        return default_value;
    } else {
        return v[f].GetInt();
    }
}

bool rapidjson_get_bool(const rapidjson::Value& v, string field,
                        bool default_value)
{
    const char* f = field.c_str();

    if ( !v.HasMember(f) || !v[f].IsBool() )
    {
        return default_value;
    } else {
        return v[f].GetBool();
    }
}

float rapidjson_get_float(const rapidjson::Value& v, string field,
                          float default_value)
{
    const char* f = field.c_str();
    
    if ( !v.HasMember(f) || !v[f].IsDouble() )
    {
        return default_value;
    } else {
        return (float)v[f].GetDouble();
    }
}