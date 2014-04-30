#ifndef __ANONADADO_API_UTILS
#define __ANONADADO_API_UTILS

#include <vector>
#include <string>
#include <iostream>

#include "rapidjson/rapidjson.h"
#include "rapidjson/document.h"
#include "rapidjson/prettywriter.h"
#include "rapidjson/filestream.h"
#include "rapidjson/stringbuffer.h"

using namespace std;

string rapidjson_get_string(const rapidjson::Value& v, string field,
                            string default_value="");

int rapidjson_get_int(const rapidjson::Value& v, string field,
                      int default_value=0);

bool rapidjson_get_bool(const rapidjson::Value& v, string field,
                        bool default_value=false);

float rapidjson_get_float(const rapidjson::Value& v, string field,
                          float default_value=0.0);

#endif