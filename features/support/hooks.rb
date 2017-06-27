Before('@courts') do
  url = 'http://0.0.0.0:8000'
  response = { result: true, message: '' }
  stub_request(:post, "#{url}/search/address").to_return(status: 200, body: response.to_json)
end

Before('@search_results') do
  url = 'http://0.0.0.0:8000'
  response = { result: true, message: '' }
  stub_request(:post, "#{url}/search/results?aol=All&postcode=ig1+2bn").to_return(status: 200, body: response.to_json)
end