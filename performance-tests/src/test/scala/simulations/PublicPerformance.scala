package simulations

import io.gatling.core.Predef._
import io.gatling.http.Predef._
import scala.concurrent.duration._
import com.typesafe.config._



class PublicPerformance extends Simulation
with HttpConfiguration
{
  val conf = ConfigFactory.load()
  val baseurl = conf.getString("baseUrl")
  val httpconf = httpProtocol.baseURL(baseurl).disableCaching

  val scenario1 = scenario("Happy Path for public")

    .exec(http("Start Session")
        .get("/search/"))

    .exec(http("Search by the Area of Law I am interested in")
        .get("/search/")
        .formParam("searchby", "aol")
        .check(status.is(200)))

    .exec(http("About your issue")
        .get("/search/aol")
        .formParam("aol", "Adoption")
        .check(status.is(200)))

    .exec(http("Your postcode")
        .get("/search/postcode?aol=Adoption")
        .formParam("postcode", "SW1H 9AJ")
        .check(status.is(200)))

    .exec(http("Search results")
        .get("/search/results?aol=Adoption&postcode=SW1H%209AJ")
        .check(status.is(200)))

    .exec(http("Search by the court address")
        .get("/search/")
        .formParam("searchby", "address")
        .check(status.is(200)))

    .exec(http("Search by city")
        .get("/search/address")
        .formParam("q", "Birmingham")
        .check(status.is(200)))

    .exec(http("Search results for Birmingham")
        .get("/search/results?q=Birmingham")
        .check(status.is(200)))

    .exec(http("Search courts by A-Z")
        .get("/courts/")
        .check(status.is(200)))

    .exec(http("Search courts by B")
        .get("/courts/B")
        .check(status.is(200)))

    .exec(http("Search by court location code")
        .get("/search/courtcode")
        .check(status.is(200)))

  val userCount = conf.getInt("users")
  val durationInSeconds  = conf.getLong("duration")

  setUp(
    scenario1.inject(rampUsers(userCount) over (durationInSeconds seconds)).protocols(httpconf)
  )
}
