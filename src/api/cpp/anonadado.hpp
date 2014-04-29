#ifndef __ANONADADO_API
#define __ANONADADO_API

#include <vector>
#include <string>

#include "rapidjson/rapidjson.h"
#include "rapidjson/document.h"
#include "rapidjson/prettywriter.h"
#include "rapidjson/filestream.h"
#include "rapidjson/stringbuffer.h"

namespace anonadado {

    class domain {
        
    };

    class annotation {
        
    };
    
    class instance {
        private:
            domain* d;
            std::vector<annotation*> annotations;

            std::string domain_name;
            std::string domain_filename;

            std::string instance_name;
            std::string instance_filename;

            std::string video_filename;
            std::string sequence_filename;
            
        public:
            instance();
            instance(domain* d);

            void read(std::string filename);
    };
};

#endif