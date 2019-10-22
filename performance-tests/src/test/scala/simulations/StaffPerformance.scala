package simulations

import io.gatling.core.Predef._
import io.gatling.http.Predef._
import scala.concurrent.duration._
import com.typesafe.config._



class StaffPerformance extends Simulation
with HttpConfiguration
{
  val conf = ConfigFactory.load()
  val baseurl = conf.getString("baseUrl")
  val httpconf = httpProtocol.baseURL(baseurl).disableCaching

  val scenario1 = scenario("Happy Path for staff")

    .exec(http("Store authenticity token")
        .get("/admin/users/sign_in")
        .check(css("input[name='csrfmiddlewaretoken']", "value").saveAs("csrfCookie")))

    .exec(http("Sign in")
        .get("/admin/users/sign_in")
        .formParam("username", conf.getString("userName"))
        .formParam("password", conf.getString("userPassword"))
        .formParam("csrfmiddlewaretoken", session => {
              session("csrfCookie").as[String]
        })
        .check(status.is(200)))

    .exec(http("Courts and tribunals")
        .get("/staff/courts")
        .check(status.is(200)))

    .exec(http("Sort courts and tribunals by last updated")
        .get("/staff/courts?sort=updated_at")
        .check(status.is(200)))
    
    .exec(http("View court")
        .get("/courts/aberdeen-employment-tribunal")
        .check(status.is(200)))

    .exec(http("Edit general court information")
        .get("/staff/court/692444")
        .formParam("name", "Test Bolton Social Security and Child Support Tribunal")
        .formParam("alert", "Test alert")
        .check(status.is(200)))

    .exec(http("Edit court type information")
        .get("/staff/court/692444/types")
        .formParam("court_types", "5331")
        .formParam("court_types", "5333")
        .formParam("number", "Test crown court code")
        .check(status.is(200)))

    .exec(http("Edit court location")
        .get("/staff/court/692444/location")
        .formParam("postcode", "SW1H 9AJ")
        .check(status.is(200)))

    .exec(http("Edit court opening times")
        .get("/staff/court/692444/opening_times")
        .formParam("form-0-hours", "Test opening times")
        .check(status.is(200)))

    .exec(http("Add new court")
        .get("/staff/court/new")
        .formParam("name", "Test new court name")
        .check(status.is(200)))

    .exec(http("Emergency message")
        .get("/staff/emergency")
        .check(status.is(200)))

    .exec(http("User management")
        .get("/staff/users")
        .check(status.is(200)))

    .exec(http("Facility types")
        .get("/staff/facility_types")
        .check(status.is(200)))
    
    .exec(http("Edit facility type")
        .get("/staff/edit_facility_type/35")
        .formParam("name", "Test baby changing")
        .check(status.is(200)))

    .exec(http("Contact types")
        .get("/staff/contact_types")
        .check(status.is(200)))

    .exec(http("Edit contact type")
        .get("/staff/edit_contact_type/27")
        .formParam("name", "Test Account")
        .check(status.is(200)))

    .exec(http("My account")
        .get("/staff/account")
        .check(status.is(200)))

  val userCount = conf.getInt("users")
  val durationInSeconds  = conf.getLong("duration")

  setUp(
    scenario1.inject(rampUsers(userCount) over (durationInSeconds seconds)).protocols(httpconf)
  )

}
