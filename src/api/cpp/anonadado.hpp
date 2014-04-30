#ifndef __ANONADADO_API
#define __ANONADADO_API

#include <iostream>
#include <string>
#include <vector>
#include <map>

#include "rapidjson/rapidjson.h"
#include "rapidjson/document.h"
#include "rapidjson/prettywriter.h"
#include "rapidjson/filestream.h"
#include "rapidjson/stringbuffer.h"

#include "utils.hpp"

using namespace std;

namespace anonadado {

    class feature {
        protected:
            std::string name;
            std::string type;
        public:
            feature();
            
            virtual void read(const rapidjson::Value& v);
            void read(std::string filename);
    };

    /* Bool Feature */
    class bool_feature : public feature {
        protected:
            bool default_value;
            bool value;


        public:
            bool_feature();
            virtual void read(const rapidjson::Value& v);

            bool get_value();
    };

    /* String Feature */
    class str_feature : public feature {
        protected:
            string default_value;
            string value;


        public:
            str_feature();
            virtual void read(const rapidjson::Value& v);

            string get_value();
    };

    /* Float Feature */
    class float_feature : public feature {
        protected:
            float default_value;
            float value;


        public:
            float_feature();
            virtual void read(const rapidjson::Value& v);

            float get_value();
    };

    /* Int Feature */
    class int_feature : public feature {
        protected:
            int default_value;
            int value;


        public:
            int_feature();
            virtual void read(const rapidjson::Value& v);

            int get_value();
    };

    /* Choice Feature */
    class choice_feature : public feature {
        protected:
            int default_value;
            int value;
            std::vector<std::string> values;
        
        public:
            choice_feature();
            virtual void read(const rapidjson::Value& v);

            string get_value();
    };
    
    // TODO: bbox_feature, vector_feature, point_feature
    
    /*************************************************************************/
    
    class annotation {
        private:
            int frame;
            std::string name;
            bool is_unique;
            bool is_global;

            std::vector<feature*> features;

        public:
            annotation();
            ~annotation();
            
            void read(const rapidjson::Value& v);
            void read(std::string filename);

            string get_name();
        private:
            void clear_features();
    };
    
    class domain {

        private:
            map<string, annotation*> labels;
            std::string name;
        
        public:
            domain();

            void read(std::string filename);
            annotation* get_instance(string label_name);

        private:
            void clear_labels();
    };
    
    class instance {
        private:
            domain* d;
            std::vector< vector<annotation*> > annotations;
            
            std::string domain_filename;
            
            std::string instance_name;
            std::string instance_filename;

            std::string video_filename;
            std::string sequence_filename;
            
        public:
            instance();
            ~instance();
            
            void read(std::string filename);

        private:
            void clear_annotations();
    };
};

#endif
