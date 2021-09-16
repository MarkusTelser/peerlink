
def trackerHTTP(addr, info_hash, peer_id, port, uploaded, downloaded, left, ip=None, event=None, numwant=None, no_peer_id=None, compact=None):
    params = ""

    # required parameters
    params += f"info_hash={info_hash}"
    params += f"&peer_id={peer_id}"
    params += f"&port={port}"
    params += f"&uploaded={uploaded}"
    params += f"&downloaded={downloaded}"
    params += f"&left={left}"
    
    # optional parameters
    if ip is not None:
        params += f"&ip={ip}"
    if event is not None:
        params += f"&event={event}"
    if numwant is not None:
        params += f"&numwant={numwant}"
    if no_peer_id is not None:
        params += "&no_peer_id={no_peer_id}"
    if compact is not None:
        params += "&compact={compact}"

    url = f"{addr}?{params}"
    recv = requests.get(url)
    
    """
    failure_code key that tracker might send back:

    100	Invalid request type: client request was not a HTTP GET.
    101	Missing info_hash.
    102	Missing peer_id.
    103	Missing port.
    150	Invalid infohash: infohash is not 20 bytes long.
    151	Invalid peerid: peerid is not 20 bytes long.
    152	Invalid numwant. Client requested more peers than allowed by tracker.
    200	info_hash not found in the database. Sent only by trackers that do not automatically include new hashes into the database.
    500	Client sent an eventless request before the specified time.
    900	Generic error.
    """
    

    print("full url: ", url)
    answer = bencode.decode(recv.text)
    print(json.dumps(answer, indent=4, sort_keys=True))
    print(recv.status_code)

    recv.close()
    
    peers = answer.get("peers")
