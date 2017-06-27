Before('@step54') do
  url = 'http://0.0.0.0:8000'
  response = { result: true, message: 'HWF-000-000' }
  stub_request(:post, "#{url}/search/address").to_return(status: 200, body: response.to_json)
end
