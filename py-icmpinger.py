import socket
import struct
import time
import argparse


def parse_cmdline_args():
    parser = argparse.ArgumentParser(description='Pings a host on the net')
    parser.add_argument('-t', '--target', type=str, dest='target', required=True,
                        help='The target host to ping on')
    parser.add_argument('--timeout', type=float, dest='max_wait', default=1,
                        help='Sets the max timeout value in seconds')
    parser.add_argument('-c', '--count', type=int, dest='count', default=4,
                        help='How many times to ping the host, defaults to 4')
    parser.add_argument('-d', '--delay', type=float, dest='delay', default=500,
                        help='Time in milliseconds between pings, defaults to 500 (ms)')
    parser.add_argument('-i', '--infinite', dest='infinite', action='store_const', const=True, default=False,
                        help='Pings without stopping, (use CTRL + C to stop)')
    parser.add_argument('-s', '--size', type=int, dest='size', default=32,
                        help='Size of the payload in bytes (the limit is 65500 bytes)')
    return parser.parse_args()


def checksum(data):
    """
        This function takes binary data (bytes), and sum them in pairs of bytes as a 16 bit value
                    In case of results larger than 16 bits, shift right as a 16 bit and add to the 16 bit sum
                    After the steps above, 1 complement the result and mask it as a 16 bit value
                    this way it avoids the number being treated as a negative number larger then 16 bits

    :param data: Any object that can be represented as bytes
    :return: Checksum of the computed data
    """
    shift_16_b_left = 256
    shift_as_16b_value = 16
    mask_as_16b = 0xffff
    data_len = len(data)
    binary_sum = 0
    for i in range(0, data_len - 1, 2):
        binary_sum += data[i] * shift_16_b_left + data[i + 1]
    # Consider overflow just as an alias for the sum, only for semantic convenience
    overflow = binary_sum
    binary_sum = ~((binary_sum & mask_as_16b) + (overflow >> shift_as_16b_value)) & mask_as_16b
    return binary_sum


def create_echo_request(payload, seq):
    """
        This function creates an ICMP echo request header, and build a complete packet, by appending the payload as data
        There is one side effect here, the local counter gets incremented each time the function is called
        Doing so will create incremental sequence numbers in the packet

    :param seq: Sequence number for the packet
    :param payload: Any data that can be represented as bytes
    :return: The complete ICMP packet as bytes
    """
    echo_request = 8
    packet_id = socket.htons(1)
    seq_num = socket.htons(seq)
    # For ICMP echo, there is no need for code, so we leave it as 0
    null_code = null_checksum = 0
    # In case of odd length payload, append a null byte (\00) at the end, making it an even number of bytes
    if len(payload) % 2 != 0:
        payload += b'\00'
    struct_fmt = 'bbHHH'
    header = struct.pack(struct_fmt, echo_request, null_code, null_checksum, packet_id, seq_num)
    pkt_checksum = checksum(header + payload)
    header = struct.pack(struct_fmt, echo_request, null_code, socket.htons(pkt_checksum), packet_id, seq_num)
    return header + payload


def create_socket(timeout):
    """
        This funcion creates a socket and binds to the local interface, using the RAW ICMP as protocol

    :param timeout: Maximum threshold in seconds, before raising a timeout error
    :return: A local interface bound socket ready to use
    """
    local_iface = ('0.0.0.0', 0)
    icmp_proto_code = socket.getprotobyname('icmp')
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp_proto_code)
    sock.settimeout(timeout)
    sock.bind(local_iface)
    return sock


def send_ping(sock, target_addr, data, seq):
    try:
        buf_size = 65565
        icmp_packet = create_echo_request(data, seq)
        start_time = time.perf_counter()
        sock.sendto(icmp_packet, target_addr)
        sock.recvfrom(buf_size)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print('Ping to {} (addr: {}) successful!'.format(args.target, target_addr[0]))
        print('Time taken: {:.07f} sec(s)'.format(total_time))
        print()
    except socket.timeout:
        print('Request timeout!')


def generate_sample_data(byte_count):
    """
        This function generates a repeated sequence of the alphabet as ascii data

    :param byte_count: Total count for the sequence
    :return: Alphabet pattern in bytes
    """
    sample = 'ABCDEFGHIJKLMNOPQRSTUVW'
    data = ''
    for i in range(byte_count):
        data += sample[i % len(sample)]
    data = data.encode('ascii')
    return data


def main():
    if args.size > 65500:
        raise ValueError('Size can\'t be greater than 65500 bytes!')
    local_sock = create_socket(abs(args.max_wait))
    interval_ms = abs(args.delay) / 1000
    payload = generate_sample_data(args.size)
    dest_addr = (socket.gethostbyname(args.target), 0)
    count = 0
    if not args.infinite:
        count = args.count
        for seq_no in range(count):
            send_ping(local_sock, dest_addr, payload, seq_no)
            time.sleep(interval_ms)
    else:
        while True:
            send_ping(local_sock, dest_addr, payload, count)
            count += 1
            time.sleep(interval_ms)


try:
    args = parse_cmdline_args()
    main()
except socket.gaierror:
    print('Could not find hostname, verify the name and try again')
except OSError as err:
    print(err)
except ValueError as err:
    print(err)
except KeyboardInterrupt:
    print('Exiting program')
