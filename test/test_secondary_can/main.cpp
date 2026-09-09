#include "../test_harness_device.h"
#include "../test_harness_native.h"
#include "../test_utils.h"
#include "globals.h"

extern bool processSecondaryCanReply(Stream &port);

class reply_stream_t : public Stream
{
public:
    uint8_t data[10] = {1, 0, 0, 0, 0, 0, 0, 0, 0x34, 0x12};
    uint8_t cursor = 0;
    uint8_t received = 0;
    uint8_t emptyReads = 0;
    int available(void) override { return received - cursor; }
    int peek(void) override { return available() ? data[cursor] : -1; }
    int read(void) override { if (available()) { return data[cursor++]; } ++emptyReads; return -1; }
    void flush(void) override {}
    size_t write(uint8_t) override { return 1; }
};

static void test_fragmented_success(void)
{
    reply_stream_t port;
    configPage9.caninput_source_start_byte[0] = 6;
    configPage9.caninput_source_num_bytes = 1;
    currentStatus.canin[0] = 42;
    for (uint8_t n = 0; n < 10; ++n)
    {
        port.received = n;
        TEST_ASSERT_FALSE(processSecondaryCanReply(port));
        TEST_ASSERT_EQUAL_UINT8(0, port.cursor);
        TEST_ASSERT_EQUAL_UINT16(42, currentStatus.canin[0]);
    }
    port.received = 10;
    TEST_ASSERT_TRUE(processSecondaryCanReply(port));
    TEST_ASSERT_EQUAL_UINT16(0x1234, currentStatus.canin[0]);
    TEST_ASSERT_EQUAL_UINT8(10, port.cursor);
    TEST_ASSERT_EQUAL_UINT8(0, port.emptyReads);
}

static void test_short_failure(void)
{
    reply_stream_t port;
    port.data[0] = 0;
    port.received = 1;
    TEST_ASSERT_FALSE(processSecondaryCanReply(port));
    port.received = 2;
    TEST_ASSERT_TRUE(processSecondaryCanReply(port));
    TEST_ASSERT_EQUAL_UINT8(2, port.cursor);
    TEST_ASSERT_EQUAL_UINT8(0, port.emptyReads);
}

static void test_invalid_channel_consumes_reply(void)
{
    reply_stream_t port;
    port.data[1] = 255;
    port.received = 10;
    currentStatus.canin[0] = 42;
    TEST_ASSERT_TRUE(processSecondaryCanReply(port));
    TEST_ASSERT_EQUAL_UINT8(10, port.cursor);
    TEST_ASSERT_EQUAL_UINT16(42, currentStatus.canin[0]);
}

void runAllTests(void)
{
    RUN_TEST_P(test_fragmented_success);
    RUN_TEST_P(test_short_failure);
    RUN_TEST_P(test_invalid_channel_consumes_reply);
}
TEST_HARNESS(runAllTests)
