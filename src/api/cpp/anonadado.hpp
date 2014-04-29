#ifndef __ANONADADO_API
#define __ANONADADO_API

#include <vector>
#include <string>
#include <iostream>

#include "rapidjson/rapidjson.h"
#include "rapidjson/document.h"
#include "rapidjson/prettywriter.h"
#include "rapidjson/filestream.h"
#include "rapidjson/stringbuffer.h"

using namespace std;

namespace anonadado {

    class domain {

        public:
            domain(){}
    };

    class annotation {
        
    };
    
    class instance {
        private:
            domain* d;
            std::vector<annotation*> annotations;
            
            std::string domain_filename;
            
            std::string instance_name;
            std::string instance_filename;

            std::string video_filename;
            std::string sequence_filename;
            
        public:
            instance();
            ~instance();
            
            void read(std::string filename);
    };
};

#endif
