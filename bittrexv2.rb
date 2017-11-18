require 'openssl'
require 'net/http'
require 'uri'
require 'base64'
require 'json'

HOST   = 'https://bittrex.com/Api/v2.0'
KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
SEC = "yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"

def jsonv2(path, params = {}, headers = {})
    nonce   = Time.now.to_i
    url     = "#{HOST}#{path}?apikey=#{KEY}&nonce=#{nonce}"
    uri     = URI(url)
    signature        = OpenSSL::HMAC.hexdigest('sha512', SEC, url)
    http             = Net::HTTP.new(uri.host, uri.port)
    http.use_ssl     = true
    http.verify_mode = OpenSSL::SSL::VERIFY_NONE
    header = {"Content-Type" => "application/json",
        "nonce" => nonce.to_s,
        "apikey"=> KEY,
        "apisign"=> signature
    }
    req = Net::HTTP::Post.new(url)
    req.initialize_http_header(header).to_json
    req.body = JSON.dump(params)
    res = http.request(req)
    puts "response #{res.body}"
end

#test = json("/key/orders/getopenorders")
test = jsonv2("/key/orders/getorderhistory")


#https://github.com/thebotguys/golang-bittrex-api/blob/master/bittrex/common.go
#https://github.com/thebotguys/golang-bittrex-api/wiki/Bittrex-API-Reference-(Unofficial)
