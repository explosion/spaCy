#ifndef NONPROJ_HH
#define NONPROJ_HH

#include <stdexcept>
#include <string>

void raise_domain_error(std::string const &msg) {
    throw std::domain_error(msg);
}

#endif // NONPROJ_HH
