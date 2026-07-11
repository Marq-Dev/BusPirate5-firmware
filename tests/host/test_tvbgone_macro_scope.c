#include <stdint.h>

#define uint8_t unsigned char
#define uint16_t unsigned int

/* This models the required cleanup immediately after tvbgone-codes.h. */
#ifndef TEST_WITH_TVBGONE_CLEANUP
#error "Compile once without cleanup to prove macro leakage"
#endif

#undef uint8_t
#undef uint16_t

typedef struct {
    uint16_t size;
    uint16_t word_size;
    uint32_t words[1];
} fixed_bitset_32_model_t;

_Static_assert(sizeof(fixed_bitset_32_model_t) == 8,
               "uint16_t macro leakage changes the SDK structure layout");

int main(void) {
    return 0;
}
